import numpy as np
import os

class FisherAnalysis:
    def __init__(self, trendy, plunge, typ_dat="Neznámy"):
        self.trendy = np.array(trendy, dtype=float)
        self.plunge = np.array(plunge, dtype=float)
        self.N = len(trendy)
        self.typ_dat = typ_dat  
        
        self.R = None       # Výsledný vektor (R)
        self.R_mean = None  # Stredný vektor (R/n)
        self.trend_vysledny = None
        self.plunge_vysledny = None
        self.kappa = None   # atribút pre pre Kappa = (n-1)/(n-R)
        self.kappa_fisher1987 = None # Špecifický odhad pre N < 16 (Fisher et al. 1987)
        self.kappa2 = None  # atribút pre pre Kappa2 = (n-2)/(n-R)
        self.kappa_est = None
        self.circular_variance = None # atribút pre pre rozptyl
        self.alpha95 = None
        self.mca = None     # atribút pre Mean Cone Angle (MCA) MCA = arccos(R/n)
        self.alpha95_priblizne = None  # atribút pre priblížny výpočet Alpha95 = 140 / (k * n)^0.5 ; platí pre N>10
        self.theta = None  # odhad pri väčšom počte dát theta = 81/(kappa)^0,5
        self.alpha99 = None # atribút pre Uhol spoľahlivosti α99 = arccos(1 - ((n-R)/R).[(1/0,01)^(1/(n-1)) - 1])
        self.suradnice_R = (0.0, 0.0, 0.0)
        self.suradnice_norm = (0.0, 0.0, 0.0)

    @classmethod
    def nacitaj_zo_suboru(cls, nazov_suboru, vybrat_typ="L"):
        """
        Načíta dáta zo súboru oddeleného tabulátorom.
        Stĺpce: ID | Typ (L/S) | Trend | Plunge | Komentár
        """
        list_trendov = []
        list_plunge = []
        
        with open(nazov_suboru, 'r', encoding='utf-8') as subor:
            for riadok in subor:
                casti = riadok.strip().split('\t')
                
                if len(casti) < 4:
                    continue
                
                typ = casti[1].strip().upper()   
                trend_str = casti[2].strip()     
                plunge_str = casti[3].strip()    
                
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
        print(f"Úspešne načítaných {len(list_trendov)} meraní pre: {oznacenie}")
        
        return cls(list_trendov, list_plunge, typ_dat=oznacenie)

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
        if self.R is None:
            self.spocitaj_smer()

        # Kontrola, aby sme nedelili nulou (ak sa N rovná R, dáta sú dokonale rovnobežné)
        menovatel = self.N - self.R

        
        if self.N > 0:
            # Výpočet Stredného vektora R/n
            self.R_mean = self.R / self.N
            # Výpočet cirkulárnej variancie (S0 = 1 - R/N)
            self.circular_variance = 1.0 - (self.R / self.N)

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
            if self.N > 2:
                self.kappa_est = (self.N - 1)**3 / ((self.N * menovatel) - menovatel**2)
            else:
                self.kappa_est = self.kappa
        

            # Špecifické vetvenie pre Kappa podľa Fisher et al. (1987) pre N<16
            if self.N < 16:
                # Malé súbory dát vyžadujú korekciu vychýlenia smerom nadol
                if self.N > 2:
                    self.kappa_fisher1987 = (self.N - 1)**3 / ((self.N * menovatel) - menovatel**2)
                else:
                    self.kappa_fisher1987 = self.kappa
            else:
                # Pre N >= 16 sa používa štandardný odhad
                self.kappa_fisher1987 = self.kappa
        else:
            self.kappa = 0.0
            self.kappa2 = 0.0
            self.kappa_est = 0.0
            self.kappa_fisher1987 = 0.0
            
        # Presný výpočet Alpha95 s hladinou významnosti (0,05)
        if self.R > 0 and self.N > 1:
            pomer = 1 - (menovatel / self.R) * ((1 / 0.05)**(1 / (self.N - 1)) - 1)
            pomer = max(-1.0, min(1.0, pomer)) 
            self.alpha95 = np.degrees(np.arccos(pomer))
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

        
        if k_pre_odhad > 0 and self.N > 0:
            self.alpha95_priblizne = 140.0 / np.sqrt(k_pre_odhad * self.N)
            self.theta = 81.0 / np.sqrt(k_pre_odhad)
        else:
            self.alpha95_priblizne = 180.0
            self.theta = 180.0
            
        # Ppriblížny výpočet: Alpha 95 = 140 / (k * n)^0.5
        if self.kappa > 0 and self.N > 0:
            self.alpha95_priblizne1 = 140.0 / np.sqrt(self.kappa * self.N)
        else:
            self.alpha95_priblizne1 = 180.0

        # Kruhová odchýlka (Theta) podla vzorca theta = 81 / (kappa)^0.5
        if self.kappa > 0:
            self.theta = 81.0 / np.sqrt(self.kappa)
        else:
            self.theta = 180.0

    def zobrazit_report(self):
        print(f"\n======================= Výpočtový REPORT Fisher Analýzy ========================")
        print(f"fisher_computing_01.py {self.typ_dat}")
        print(f"Počet meraní (n):                                  {self.N}")
        print(f"Dĺžka výsledného vektora R (Resultant Vector):     {self.R:.4f}")
        print(f"Stredný vektor (Mean Vector):                      {self.R_mean:.4f}")
        print(f"Výsledný Azimut/TREND:                             {self.trend_vysledny:.1f}°")
        print(f"Výsledný Sklon/PLUNGE:                             {self.plunge_vysledny:.1f}°")
        print(f"--------------------------------------------------------------------------------")
        print(f"SÚRADNICE VÝSLEDNÉHO VEKTORA (R): Σx = {self.suradnice_R[0]:.4f}, Σy = {self.suradnice_R[1]:.4f}, Σz = {self.suradnice_R[2]:.4f}")
        print(f"ZNORMALIZOVANÉ SÚRADNICE (Dĺžka = 1): x = {self.suradnice_norm[0]:.4f}, y = {self.suradnice_norm[1]:.4f}, z = {self.suradnice_norm[2]:.4f}")
##        print(f"  x: {self.suradnice_norm[0]:.4f}")
##        print(f"  y: {self.suradnice_norm[1]:.4f}")
##        print(f"  z: {self.suradnice_norm[2]:.4f}")
        print(f"--------------------------------------------------------------------------------")
        print(f"Cirkulárna variancia Cirkular variance S₀ = 1 - (R/n) :             {self.circular_variance:.4f}")
        print(f"Parameter koncentrácie κ; Kappa = (n-1)/(n-R):                      {self.kappa:.2f}")
        print(f"Parameter koncentrácie κ2; Kappa2 = (n-2)/(n-R):                    {self.kappa2:.2f}")
        print(f"Predbežný odhad κ (n < 30):                                         {self.kappa_est:.2f}")
        # prehľadné zobrazenie podmienky Fisher et al. 1987
        status_n = f"Aktivovaná korekcia pre n={self.N} (n<16)" if self.N < 16 else f"Štandardný odhad pre n={self.N} (n>=16)"
        print(f"κ podľa Fisher et al. (1987) ({status_n}):  {self.kappa_fisher1987:.2f}")

        print(f"Uhol spoľahlivosti α95:                                             {self.alpha95:.2f}°")
        print(f"Uhol α95 (približný odhad platný iba pre n>10) α95 = 140/(k*n)^0.5: {self.alpha95_priblizne1:.2f}°")
        print(f"Mean Cone Angle (MCA) MCA = arccos(R/n):                            {self.mca:.2f}°")
        print(f"Kruhová odchýlka Spherical Aperture theta θ = 81/(kappa)^0,5:       {self.theta:.2f}°")
        print(f"Uhol spoľahlivosti α99 ")
        print(f"      α99 = arccos(1 - ((n-R)/R).[(1/0,01)^(1/(n-1)) - 1]):         {self.alpha99:.2f}°")
        print(f"================================================================================")
        print(f"================================================================================\n")

# --- SPÚŠŤACIA ČASŤ ---
nazov_suboru = os.path.join("../examples", "Lineations_37k.tsv")  #  "../examples", "Lineations.tsv" iny: "../../data_", "data_1.txt"

try:
    # 1. ANALÝZA PLÔCH (S)
    print(f"Načítavam plochy zo súboru: {nazov_suboru}")
    analyza_ploch = FisherAnalysis.nacitaj_zo_suboru(nazov_suboru, vybrat_typ="S")
    analyza_ploch.vypocitaj_fishera()
    analyza_ploch.zobrazit_report()

    # 2. ANALÝZA LINEÁCIÍ (L)
    print(f"Načítavam lineácie zo súboru: {nazov_suboru}")
    analyza_lineacii = FisherAnalysis.nacitaj_zo_suboru(nazov_suboru, vybrat_typ="L")
    analyza_lineacii.vypocitaj_fishera()
    analyza_lineacii.zobrazit_report()

except FileNotFoundError:
    print(f"\n[CHYBA] Súbor sa nenašiel!")
    print(f"Hľadal som ho na adrese: {os.path.abspath(nazov_suboru)}")
