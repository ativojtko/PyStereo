import numpy as np
import os
import sys  # Pridajte import sys, ak tam ešte nie je

# Natvrdo prinútime konzolový výstup tohto skriptu komunikovať v UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    
class FisherAnalysis:
    def __init__(self, trendy, plunge, typ_dat="Neznámy", obsahuje_plochy=False):
        self.trendy = np.array(trendy, dtype=float)
        self.plunge = np.array(plunge, dtype=float)
        self.N = len(trendy)
        self.typ_dat = typ_dat
        self.obsahuje_plochy = obsahuje_plochy  # Atribút na detekciu prítomnosti plôch
        
        self.R = None       # Výsledný vektor (R)
        self.R_mean = None  # Stredný vektor (R/n)
        self.trend_vysledny = None
        self.plunge_vysledny = None
        self.kappa = None   # atribút pre pre Kappa = (n-1)/(n-R)
        self.kappa_fisher1987 = None # Špecifický odhad pre N < 16 (Fisher et al. 1987)
        self.kappa2 = None  # atribút pre pre Kappa2 = (n-2)/(n-R)
        self.kappa_est = None 
        self.kappa_aktivna = None
        self.kappa50 = None # atribút pre Kappa50 = (n)/(n-R)
        self.circular_variance = None # atribút pre pre rozptyl
        self.s_rad = None # atribút pre Uhlová štandardná odchýlka (Angular Standard Deviation) s = (2*(1-(R/n)))^0,5
        self.s_deg = None
        self.alpha95 = None
        self.mca = None     # atribút pre Mean Cone Angle (MCA) MCA = arccos(R/n)
        self.alpha95approx_rad = None #  Približné α95 = (5,9914.(n-R)/n.R)^0,5
        self.alpha95_priblizne = None  # atribút pre priblížny výpočet Alpha95 = 140 / (k * n)^0.5 ; platí pre N>10
        self.alpha95_priblizne1 = None  # atribút pre priblížny výpočet Alpha95 = 140 / (k odhad pre fisher pri n<16) * n)^0.5 ; platí pre N>10
        self.theta = None  # odhad pri väčšom počte dát theta = 81/(kappa)^0,5
        self.alpha99 = None # atribút pre Uhol spoľahlivosti α99 = arccos(1 - ((n-R)/R).[(1/0,01)^(1/(n-1)) - 1])
        self.suradnice_R = (0.0, 0.0, 0.0)
        self.suradnice_norm = (0.0, 0.0, 0.0)
        self.argumentA93 = None  # pre Alpha93 cez ln a Cp
        self.argumentA95 = None  # pre Alpha95 cez ln a Cp
        self.argumentA99 = None  # pre Alpha99 cez ln a Cp
        self.Cp93 = None # koeficient pravdepodobnosti pre alpha93
        self.Cp95 = None # koeficient pravdepodobnosti pre alpha95
        self.Cp99 = None # koeficient pravdepodobnosti pre alpha99
##        alpha93_deg = None
##        alpha95_deg = None
##        alpha99_deg = None
##        alpha93_rad = None
##        alpha95_rad = None
##        alpha99_rad = None

    @classmethod
    def nacitaj_zo_suboru(cls, nazov_suboru, vybrat_typ="L"):
        """
        Načíta dáta zo súboru oddeleného tabulátorom.
        Stĺpce: ID | Typ (L/S) | Trend | Plunge | Komentár
        """
        list_trendov = []
        list_plunge = []
        nasli_sa_plochy = False  # Pomocná premenná pre kontrolu celého súboru ohľadom plôch
        
        with open(nazov_suboru, 'r', encoding='utf-8') as subor:
            for riadok in subor:
                casti = riadok.strip().split('\t')
                
                if len(casti) < 4:
                    continue
                
                typ = casti[1].strip().upper()   
                trend_str = casti[2].strip()     
                plunge_str = casti[3].strip()

                # Kontrola, či sa v súbore nachádza aspoň jedna plocha (S)
                if typ == "S":
                    nasli_sa_plochy = True
                
                if typ != vybrat_typ.upper():
                    continue
                
                try:
                    tr = float(trend_str)
                    pl = float(plunge_str)
                    list_trendov.append(tr)
                    list_plunge.append(pl)
                except ValueError:
                    continue
        
        oznacenie = "Linácie (L)" if vybrat_typ.upper() == "L" else "Plochy (S)"

        if len(list_trendov) == 0:
            print(f"[UPOZORNENIE] V súbore sa nenachádzajú žiadne merania pre typ: {oznacenie}")
            return None

        print(f"Úspešne načítaných {len(list_trendov)} meraní pre: {oznacenie}")
        # Odovzdávame informáciu o prítomnosti plôch do konštruktora triedy (obsahuje_plochy=nasli_sa_plochy)
        return cls(list_trendov, list_plunge, typ_dat=oznacenie, obsahuje_plochy=nasli_sa_plochy)

    def spocitaj_smer(self):
        tr_rad = np.radians(self.trendy)
        pl_rad = np.radians(self.plunge)
        
        X_sum = np.sum(np.cos(pl_rad) * np.cos(tr_rad))
        Y_sum = np.sum(np.cos(pl_rad) * np.sin(tr_rad))
        Z_sum = np.sum(np.sin(pl_rad))

        # Uloženie súradníc výsledného stredného vektora (R)
        self.suradnice_R = (X_sum, Y_sum, Z_sum)

        # Výpočet dĺžky výsledného vektora R
        self.R = np.sqrt(X_sum**2 + Y_sum**2 + Z_sum**2)

        # Výpočet znormalizovaných súradníc (dĺžka vektora = 1)
        if self.R > 0:
            self.suradnice_norm = (X_sum / self.R, Y_sum / self.R, Z_sum / self.R)
        else:
            self.suradnice_norm = (0.0, 0.0, 0.0)
        
        # Prevod smerov stredného vektora späť na geologické stupne
        if self.R > 0:
            self.plunge_vysledny = np.degrees(np.arcsin(Z_sum / self.R))
            self.trend_vysledny = np.degrees(np.arctan2(Y_sum / self.R, X_sum / self.R)) % 360
        else:
            self.plunge_vysledny = 0.0
            self.trend_vysledny = 0.0


    def vypocitaj_fishera(self):
        if self.N == 0 or self.R == 0:
            raise ValueError("Neplatné vstupné hodnoty.")
        
        if self.R is None:
            self.spocitaj_smer()

        # Kontrola, aby sme nedelili nulou (ak sa N rovná R, dáta sú dokonale rovnobežné a sú súhlasne orientované, rovnako veľké, sú kolineárne)
        menovatel = self.N - self.R

        
        if self.N > 0:
            # Výpočet Stredného vektora R/n
            self.R_mean = self.R / self.N
            # Výpočet cirkulárnej variancie (S0 = 1 - R/N)
            self.circular_variance = 1.0 - (self.R / self.N)
            # Výpočet Uhlová štandardná odchýlka (Angular Standard Deviation) s = (2 * (1 - (R/n)))^0.5 kompletne cez NumPy nástroje
            self.s_rad = np.sqrt(2 * (1 - (self.R / self.N)))
        
            # Prevod z radiánov na stupne cez NumPy funkciu np.degrees
            self.s_deg = np.degrees(self.s_rad)
       
            # return self.s_rad, self.s_deg

    
            # Výpočet MCA = arccos(R/n) premenený na stupne
            pomer_mca = max(-1.0, min(1.0, self.R_mean))
            self.mca = np.degrees(np.arccos(pomer_mca))
        else:
            self.R_mean = 0.0
            self.circular_variance = 1.0
            self.mca = 90.0       

            
        if self.N > 1 and menovatel > 0:
            # 1. Klasická kappa
            self.kappa = (self.N - 1) / menovatel
            
            # 2. kappa2 = (n-2) / (n-R)
            self.kappa2 = (self.N - 2) / menovatel
            
            # 3. Pôvodný priebežný odhad kappa
            if self.N < 30:
                self.kappa_est = (self.N - 1)**3 / (self.R * menovatel)
            else:
                self.kappa_est = (self.N - 1)**3 / (self.R * menovatel) # self.kappa_est = 0.0

            # 4. kappa50 = (n) / (n-R) Asymptotické počítanie Kappa50 pre N > 50 
            if self.N > 50:
                self.kappa50 = (self.N) / menovatel
            else:
                self.kappa50 = (self.N) / menovatel

##### Tvoj kod :)
            # Špecifické vetvenie pre Kappa podľa Fisher et al. (1987) pre N<16
            # if self.N < 16:
            #     # Malé súbory dát vyžadujú korekciu vychýlenia smerom nadol
            #     if self.N > 2:
            #         self.kappa_fisher1987 = (self.N - 1)**3 / ((self.N * menovatel) - menovatel**2)
            #     else:
            #         self.kappa_fisher1987 = (self.N - 1)**3 / ((self.N * menovatel) - menovatel**2)
            # else:
            #     # Pre N >= 16 sa používa štandardný odhad
            #     self.kappa_fisher1987 = (self.N - 1)**3 / ((self.N * menovatel) - menovatel**2) # Pre N >= 16 sa používa štandardný odhad self.kappa
########



##### Moja vsuvka kodu:) 
            if self.N in range(3, 16):
                self.kappa_fisher1987 = ((self.N - 1)**2) / (self.N * menovatel)
            else:
                self.kappa_fisher1987 = ((self.N - 1)**2) / (self.N * menovatel)

#####

        else:
            self.kappa = 0.0
            self.kappa2 = 0.0
            self.kappa_est = 0.0
            self.kappa50 = 0.0
            self.kappa_fisher1987 = 0.0
            
        # Presný výpočet Alpha95 s hladinou významnosti (0,05)
        if self.R > 0 and self.N > 1:
            pomer95 = 1 - (menovatel / self.R) * ((1 / 0.05)**(1 / (self.N - 1)) - 1)
            pomer95 = max(-1.0, min(1.0, pomer95)) 
            self.alpha95 = np.degrees(np.arccos(pomer95))
        else:
            self.alpha95 = 180.0


        # Presný výpočet Alpha99 s hladinou významnosti (0,01) 
        if self.R > 0 and self.N > 1:
            pomer99 = 1 - (menovatel / self.R) * ((1 / 0.01)**(1 / (self.N - 1)) - 1)
            pomer99 = max(-1.0, min(1.0, pomer99)) 
            self.alpha99 = np.degrees(np.arccos(pomer99))
        else:
            self.alpha99 = 180.0


        # Pre odhad α95_priblizne a theta použijeme korigovanú kappu pre presnejšie výsledky pri malom N
        k_pre_odhad = self.kappa_fisher1987 if self.kappa_fisher1987 > 0 else self.kappa

                
        if k_pre_odhad > 0 and self.N > 0 and self.R > 0:
            
            self.alpha95approx_rad = np.degrees(np.sqrt((5.9914 * (self.N - self.R)) / (self.N * self.R)))
            self.alpha95_priblizne = 140.0 / np.sqrt(self.kappa * self.N)
            self.theta = 81.0 / np.sqrt(k_pre_odhad)
        else:
            self.alpha95approx_rad = 180.0
            self.alpha95_priblizne = 180.0
            self.theta = 180.0

        # Priblížny výpočet: Alpha 95 = 140 / (k * n)^0.5, platnosť len pre n musí byť väčšie ako 10 a kappa väčšia ako 3
        if self.kappa > 0 and self.N > 0:
            self.alpha95_priblizne1 = 140.0 / np.sqrt(k_pre_odhad * self.N) # nezmysel, len pre názornosť: 
            # Kruhová odchýlka (Theta) podla vzorca theta = 81 / (kappa)^0.5
            self.theta = 81.0 / np.sqrt(self.kappa) 
        else:
            self.alpha95_priblizne1 = 180.0
            self.theta = 180.0

        # return np.degrees(self.alpha95approx_rad)



        # iné výpočty pre alpha cez ln
        if self.kappa > 0 and self.N > 0:
            # 1. Výpočet Cp93 podľa vzťahu pre 93%
            self.Cp93 = -np.log(1 - 0.93)
            # 1b. Výpočet Cp95 podľa vzťahu pre 95%
            self.Cp95 = -np.log(1 - 0.95)
            # 1c. Výpočet Cp99 podľa vzťahu pre 99%
            self.Cp99 = -np.log(1 - 0.99)
            
            # 2. Výpočet vnútrajšku zátvorky pre Alpha93
            self.argumentA93 = 1 - ((self.N - self.R) / self.R) * (self.Cp93 / self.N)
            self.argumentA95 = 1 - ((self.N - self.R) / self.R) * (self.Cp95 / self.N)
            self.argumentA99 = 1 - ((self.N - self.R) / self.R) * (self.Cp99 / self.N)
    
            # Bezpečnostná kontrola argumentu
            self.argumentA93 = np.clip(self.argumentA93, -1.0, 1.0)
            self.argumentA95 = np.clip(self.argumentA95, -1.0, 1.0)
            self.argumentA99 = np.clip(self.argumentA99, -1.0, 1.0)
    
            # 3. Výpočet arccos (výsledok v radiánoch)
            alpha93_rad = np.arccos(self.argumentA93)
            alpha95_rad = np.arccos(self.argumentA95)
            alpha99_rad = np.arccos(self.argumentA99)
    
            # 4. Prevod na stupne a ULOŽENIE DO OBJEKTU (OPRAVENÉ: pridané self.alpha93_deg)
            self.alpha93_deg = np.degrees(alpha93_rad)
            self.alpha95_deg = np.degrees(alpha95_rad)
            self.alpha99_deg = np.degrees(alpha99_rad)
            
            return {
                "Cp93": self.Cp93,
                "Alpha93_stupne": self.alpha93_deg
            }

            return {
                "Cp95": self.Cp93,
                "Alpha95_stupne": self.alpha95_deg
            }
            return {
                "Cp99": self.Cp93,
                "Alpha99_stupne": self.alpha99_deg
            }
            
        # Ošetrenie stavu, ak podmienka 'if' nie je splnená
        self.Cp93 = 0.0
        self.alpha93_deg = 0.0
        self.Cp95 = 0.0
        self.alpha95_deg = 0.0
        self.Cp99 = 0.0
        self.alpha99_deg = 0.0
        return {
            "Cp93": 0.0,
            "Alpha93_stupne": 0.0,
            "Cp95": 0.0,
            "Alpha95_stupne": 0.0,
            "Cp99": 0.0,
            "Alpha99_stupne": 0.0,

        }
            

    def zobrazit_report(self):
        
        print(f"\n======================== Výpočtový REPORT Fisher Analýzy ========================")
        print(f"Fisher_analysis_v01_05.py | {self.typ_dat}")

        # Podmienka, ktorá do reportu vloží oznam o nájdených plochách v súbore
        if self.obsahuje_plochy:
            print(f"OZNAM: Načítaný súbor obsahuje aj plochy, Fisher analýzu počítam len z obsiahnutých Lineácií.")
            print(f"--------------------------------------*********------------------------------------")
        print(f"Počet meraní (n):                                     {self.N}")
        print(f"Dĺžka výsledného vektora R (Resultant Vector):        {self.R:.4f}")
        print(f"Stredný vektor (Mean Vector):                         {self.R_mean:.4f}")
        print(f"Výsledný Azimut/TREND:                                {self.trend_vysledny:.1f}°")
        print(f"Výsledný Sklon/PLUNGE:                                {self.plunge_vysledny:.1f}°")
        print(f"---------------------------------------------------------------------------------")
        print(f"SÚRADNICE VÝSLEDNÉHO VEKTORA (R): \u03a3x = {self.suradnice_R[0]:.4f}, \u03a3y = {self.suradnice_R[1]:.4f}, \u03a3z = {self.suradnice_R[2]:.4f}")
        print(f"ZNORMALIZOVANÉ SÚRADNICE (Dĺžka = 1): x = {self.suradnice_norm[0]:.4f}, y = {self.suradnice_norm[1]:.4f}, z = {self.suradnice_norm[2]:.4f}")
##        print(f"  x: {self.suradnice_norm[0]:.4f}")
##        print(f"  y: {self.suradnice_norm[1]:.4f}")
##        print(f"  z: {self.suradnice_norm[2]:.4f}")
       
        print(f"---------------------------------------------------------------------------------")
        print(f"Cirkulárna variancia (Circular variance) S₀ = 1 - (R/n):                  {self.circular_variance:.4f}")
        print(f"Uhlová štand. odchýlka (Angular St. Dev.) s =(2*(1-(R/n)))^0,5*(180/PI):  {self.s_deg:.4f}°")
        
        print(f"---------------------------------------------------------------------------------")
        print(f'Pre zadané n = {self.N} boli vyhodnotené tieto špecifické parametre:\n')
        
        if self.N < 16:
            print(f"Predbežný odhad κ (n < 30) kappa_est = (n-1)^3/R(n-R):                  {self.kappa_est:.2f}")
            print(f"Parameter koncentrácie (Fisher et al. 1987):                            {self.kappa_fisher1987:.2f}")
            self.kappa_aktivna = self.kappa_fisher1987
            
        elif self.N in range (16, 50):
            print(f"Parameter koncentrácie κ; Kappa = (n-1)/(n-R):                              {self.kappa:.2f}")
            print(f"Parameter koncentrácie κ2; Kappa2 = (n-2)/(n-R):                            {self.kappa2:.2f}")
            
            if self.N < 30:
                print(f"Predbežný odhad κ (n < 30) kappa_est = (n-1)^3/R(n-R):                     {self.kappa_est:.2f}")
            self.kappa_aktivna = self.kappa
            
        elif self.N >= 50:
            print(f"Parameter koncentrácie κ50 pre (n>50) Kappa50 = (n)/(n-R):              {self.kappa50:.2f}")
            self.kappa_aktivna = self.kappa50
        
        
        if self.kappa_aktivna > 3 and self.N > 10:
            print(f"Uhol α95 (približný odhad platný iba pre n>10) α95 = 140/(k.n)^0.5:     {self.alpha95_priblizne:.2f}°")
            print(f"Uhol α95 (približný odhad pre n>10) α95 = 140/(k_Fisher.n)^0.5:         {self.alpha95_priblizne1:.2f}°")
            print(f"Uhol α95 (približný iba pre n>10) α95 = (5,9914.(n-R)/(n.R))^0,5:       {self.alpha95approx_rad:.2f}°")
            
        
        if self.kappa_aktivna > 5:
            print(f"Mean Cone Angle (MCA) MCA = arccos(R/n):                                {self.mca:.4f}°")
            
            
        print(f"---------------------------------------------------------------------------------")
        print(f"Kruhová odchýlka Spherical Aperture theta θ = 81/(kappa)^0,5:              {self.theta:.2f}°")
        print(f"Stredný uhol kužeľa α95 = arccos(1 - ((n-R)/R).[(1/0,05)^(1/(n-1)) - 1]):  {self.alpha95:.2f}°")
        print(f"Stredný uhol kužeľa α99 = arccos(1 - ((n-R)/R).[(1/0,01)^(1/(n-1)) - 1]):  {self.alpha99:.2f}°")
           
        print(f"Uhol α93:  Cp93​ = −ln(1−0.93)  α93 = arccos(1 - ((n-R)/R).(Cp/n)):         {self.alpha93_deg:.2f}°")
        print(f"Uhol α95:  Cp95​ = −ln(1−0.95)  α95 = arccos(1 - ((n-R)/R).(Cp/n)):         {self.alpha95_deg:.2f}°")
        print(f"Uhol α99:  Cp99​ = −ln(1−0.99)  α99 = arccos(1 - ((n-R)/R).(Cp/n)):         {self.alpha99_deg:.2f}°")
        print(f"=================================================================================")
        print(f"=================================================================================")

# --- SPÚŠŤACIA ČASŤ ---
####nazov_suboru = os.path.join("..\examples", "Lineations_17_low_kappa.tsv")  #  "../examples", "Lineations_17.tsv" iny: "../../data_", "data_1.txt"

####try:
##    # 1. ANALÝZA PLÔCH (S)
##    print(f"Načítavam plochy zo súboru: {nazov_suboru}")
##    analyza_ploch = FisherAnalysis.nacitaj_zo_suboru(nazov_suboru, vybrat_typ="S")
##    analyza_ploch.vypocitaj_fishera()
##    analyza_ploch.zobrazit_report()

####    # 2. ANALÝZA LINEÁCIÍ (L)
####    print(f"\nNačítavam lineácie zo súboru: {nazov_suboru}")
####    analyza_lineacii = FisherAnalysis.nacitaj_zo_suboru(nazov_suboru, vybrat_typ="L")
####
####    # Spustíme výpočty a report len vtedy, keď sa načítali nejaké lineácie
####    if analyza_lineacii is not None:
####        analyza_lineacii.vypocitaj_fishera()
####        analyza_lineacii.zobrazit_report()
####
####except FileNotFoundError:
####    print(f"\n[CHYBA] Súbor sa nenašiel!")
####    print(f"Hľadal som ho na adrese: {os.path.abspath(nazov_suboru)}")


###### ------- ÚPLNÝ ZÁVER SÚBORU --------- ######
# ********************************************** #
if __name__ == "__main__":
    import sys
    import os
    
    print("=================================================================================")
    print("                   ŠTATISTICKÝ MODUL: FISHER ANALYSIS v.01.05                    ")
    print("=================================================================================")
    print(f"Spustené z interpretora: {sys.executable}")
    print(f"Vstupné argumenty (sys.argv): {sys.argv}\n")

    nazov_suboru = None

    # Bezpečné vytiahnutie argumentu z hlavného GUI
    try:
        if len(sys.argv) > 1:
            nazov_suboru = sys.argv[1]  # Použije presnú cestu odovzdanú z GUI
    except Exception as e:
        print(f"[VAROVANIE]: Nepodarilo sa prečítať sys.argv: {e}")

    # AK NEBOL ZADANÝ ARGUMENT Z GUI (ZÁLOŽNÝ REŽIM)
    if not nazov_suboru:
        print("[INFO]: Nebol detegovaný argument z GUI. Hľadám záložný súbor...")
        
        # Zistíme, kde fyzicky leží tento skript (čiže root/statistics)
        adresar_skriptu = os.path.dirname(os.path.abspath(__file__))
        
        # Odvodíme absolútnu cestu k rootu (statistics/.. -> root)
        adresar_root = os.path.abspath(os.path.join(adresar_skriptu, ".."))
        
        # Zostavíme definitívnu absolútnu cestu k záložnému súboru (root/examples/Lineations_17.tsv)
        cesta_k_zalrhe = os.path.join(adresar_root, "examples", "Lineations_17.tsv")
        nazov_suboru = os.path.abspath(cesta_k_zalrhe)

    print(f"Cieľový súbor na spracovanie:\n-> {nazov_suboru}\n")

    # Samotný výpočet
    try:
        if not os.path.exists(nazov_suboru):
            print(f"[CHYBA]: Súbor fyzicky NEEXISTUJE na disku!")
            print(f"Hľadané na trase: {nazov_suboru}")
        else:
            print("Štartujem čítanie dát...")
            analyza_lineacii = FisherAnalysis.nacitaj_zo_suboru(nazov_suboru, vybrat_typ="L")
            
            if analyza_lineacii is not None:
                print("Dáta úspešne načítané. Spúšťam Fisherovu štatistiku...")
                analyza_lineacii.vypocitaj_fishera()
                analyza_lineacii.zobrazit_report()
            else:
                print("[UPOZORNENIE]: Žiadne lineácie (L) sa v súbore nenašli.")
                
    except Exception as e:
        import traceback
        print("\n!!! VYSKYTLA SA CHYBA PRI BEHU PROGRAMU !!!")
        print(f"Typ chyby: {e}")
        traceback.print_exc()
        
    # print("\n================================================================================")
    # input("Stlačením klávesu ENTER zatvoríte toto okno...")
