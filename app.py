import streamlit as st
import pandas as pd

# ==========================================
# 1. CONFIGURARE PAGINĂ & CSS PREMIUM
# ==========================================
st.set_page_config(
    page_title="Mentor Financiar Pro - Salon Beauty",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    /* Fundal general si tipografie */
    .stApp { background-color: #FAFAFA; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Casete explicative (Varianta B - Ghidaje) */
    .explaining-note {
        background-color: #FFF2F6;
        border-left: 4px solid #D11A5B;
        padding: 10px 14px;
        border-radius: 0px 8px 8px 0px;
        margin-top: -12px;
        margin-bottom: 20px;
        font-size: 0.85rem;
        color: #4A4A4A;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.02);
    }
    
    /* Design panouri metrice */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        border-top: 4px solid #D11A5B;
    }
    
    /* Stiluri Butoane Navigare */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. STATE MANAGEMENT (Baza de date in RAM)
# ==========================================
if 'step' not in st.session_state: st.session_state.step = 1
if 'fiscal' not in st.session_state: st.session_state.fiscal = {'forma': 'SRL - Profit (16%)', 'tva': 'Neplătitor', 'target_net': 15000.0}
if 'tehnicieni' not in st.session_state: st.session_state.tehnicieni = []
if 'camere' not in st.session_state: st.session_state.camere = []
if 'echipamente' not in st.session_state: st.session_state.echipamente = []
if 'catalog_servicii' not in st.session_state: st.session_state.catalog_servicii = []

def set_step(n): st.session_state.step = n

# Antet Wizard
st.title("💼 Mentor Financiar Pro: Sistem de Pricing & Audit")
st.progress(st.session_state.step / 6.0)

# Meniu de navigare rapida sus
cols_nav = st.columns(6)
steps_names = ["1. Fiscal", "2. Echipa", "3. Regie", "4. Echipamente", "5. Deviz", "6. Catalog"]
for i, col in enumerate(cols_nav):
    with col:
        if st.button(steps_names[i], key=f"nav_{i+1}", use_container_width=True, type="primary" if st.session_state.step == i+1 else "secondary"):
            set_step(i+1)

st.markdown("---")

# ==========================================
# ETAPA 1: MATRICE FISCALĂ
# ==========================================
if st.session_state.step == 1:
    st.header("Etapa 1: Setări Macro-Fiscale")
    
    col1, col2 = st.columns(2)
    with col1:
        st.session_state.fiscal['forma'] = st.selectbox("Formă de organizare (Impozit pe afacere):", ["SRL - Micro (1%)", "SRL - Micro (3%)", "SRL - Profit (16%)", "PFA / II (Sistem Real)"], index=["SRL - Micro (1%)", "SRL - Micro (3%)", "SRL - Profit (16%)", "PFA / II (Sistem Real)"].index(st.session_state.fiscal['forma']))
        st.markdown('<div class="explaining-note"><b>ℹ️ Impact Fiscal:</b> Definește ce procent din deviz se va duce la stat. SRL 1% necesită un CIM full-time.</div>', unsafe_allow_html=True)
        
        st.session_state.fiscal['tva'] = st.radio("Regim TVA:", ["Neplătitor", "Plătitor (19%)"], index=0 if st.session_state.fiscal['tva'] == "Neplătitor" else 1)
        st.markdown('<div class="explaining-note"><b>ℹ️ Impact Preț:</b> Plătitorii de TVA vor avea prețul la raft automat majorat cu 19% (taxă colectată, nu profit).</div>', unsafe_allow_html=True)

    with col2:
        st.session_state.fiscal['target_net'] = st.number_input("Venit NET Tinta Proprietar (RON/lună):", min_value=0.0, value=st.session_state.fiscal['target_net'], step=1000.0)
        st.markdown('<div class="explaining-note"><b>ℹ️ Optimizare Dividende:</b> Profitul dorit în mână. Aplicația calculează brutul necesar acoperirii impozitului pe dividende de 8%.</div>', unsafe_allow_html=True)
        
        brut_necesar = st.session_state.fiscal['target_net'] / 0.92
        st.info(f"⚖️ **Obiectiv Profit Brut Firmă:** {brut_necesar:,.2f} RON (înainte de CASS dividende).")

    st.button("Salvează și treci la Etapa 2 ➡️", on_click=set_step, args=(2,), type="primary")

# ==========================================
# ETAPA 2: PROFILURI PERSONAL (Fine-Tuning)
# ==========================================
elif st.session_state.step == 2:
    st.header("Etapa 2: Baza de date Tehnicieni (CIM 2026)")
    st.markdown("Adaugă tipologiile de personal pentru a diferenția costurile per procedură.")
    
    with st.form("form_tech"):
        c1, c2, c3 = st.columns(3)
        nume_tech = c1.text_input("Nume Profil (ex: Junior, Senior, Master):")
        salariu_net = c2.number_input("Salariu NET bază garantat (RON/lună):", min_value=1.0, value=4000.0)
        ore_luna = c3.number_input("Ore lucrate pe lună:", min_value=1, value=168)
        
        if st.form_submit_button("➕ Adaugă Profil Tehnician"):
            # Gross up salarial 2026
            brut = salariu_net / 0.585
            cam = brut * 0.0225
            cost_total = brut + cam
            st.session_state.tehnicieni.append({
                "Nume": nume_tech, "Net": salariu_net, "Brut Real": round(brut, 2), 
                "Cost Firmă": round(cost_total, 2), "Cost/Minut": round(cost_total / (ore_luna * 60), 4)
            })
            st.success(f"Profilul {nume_tech} a fost adăugat!")
            
    if st.session_state.tehnicieni:
        st.dataframe(pd.DataFrame(st.session_state.tehnicieni), use_container_width=True)
        
    st.button("Salvează și treci la Etapa 3 ➡️", on_click=set_step, args=(3,), type="primary")

# ==========================================
# ETAPA 3: REGIE ȘI SPAȚII (Fine-Tuning Ineficiență)
# ==========================================
elif st.session_state.step == 3:
    st.header("Etapa 3: Regie și Posturi de Lucru")
    
    regie_totala = st.number_input("Costuri FIXE Globale (Chirie, Utilități, Marketing, Receptie - RON/lună):", value=15000.0, step=1000.0)
    st.markdown('<div class="explaining-note"><b>ℹ️ Centru Cost:</b> Regia totală a clădirii se va împărți automat (egal) la numărul de posturi de lucru adăugate mai jos.</div>', unsafe_allow_html=True)
    
    with st.form("form_camere"):
        c1, c2, c3 = st.columns(3)
        nume_cam = c1.text_input("Nume Spațiu/Post (ex: Scaun Coafură 1, Cabină Laser):")
        ore_totale = c2.number_input("Capacitate max. teoretică (ore/lună):", value=200)
        grad_ocupare = c3.slider("Grad de ocupare estimat (%):", 1, 100, 65)
        
        if st.form_submit_button("➕ Adaugă Spațiu de Lucru"):
            st.session_state.camere.append({
                "Nume": nume_cam, "Ore Teoretice": ore_totale, "Ocupare %": grad_ocupare
            })
            
    if st.session_state.camere:
        # Recalculam costul pe minut pentru fiecare camera in functie de regie
        cota_regie_per_camera = regie_totala / len(st.session_state.camere)
        afisaj_camere = []
        for cam in st.session_state.camere:
            min_teoretice = cam['Ore Teoretice'] * 60
            min_productive = min_teoretice * (cam['Ocupare %'] / 100.0)
            
            cost_ideal = cota_regie_per_camera / min_teoretice if min_teoretice > 0 else 0
            cost_real = cota_regie_per_camera / min_productive if min_productive > 0 else 0
            cost_stationare = cost_real - cost_ideal # Ineficienta platita de client
            
            cam['Cost/Minut'] = cost_real
            cam['Cost Ineficienta/Minut'] = cost_stationare
            
            afisaj_camere.append({
                "Spațiu": cam['Nume'], "Cota Regie": round(cota_regie_per_camera, 2),
                "Minute Bune": min_productive, "Cost Real/Min": round(cost_real, 4),
                "Penalizare Ocupare (Cost Staționare/Min)": round(cost_stationare, 4)
            })
        st.dataframe(pd.DataFrame(afisaj_camere), use_container_width=True)
        
    st.button("Salvează și treci la Etapa 4 ➡️", on_click=set_step, args=(4,), type="primary")

# ==========================================
# ETAPA 4: AMORTIZARE ECHIPAMENTE
# ==========================================
elif st.session_state.step == 4:
    st.header("Etapa 4: Amortizare Aparatură (CAPEX)")
    
    with st.form("form_echipamente"):
        c1, c2, c3 = st.columns(3)
        nume_eq = c1.text_input("Nume Aparat:")
        valoare = c2.number_input("Valoare Achiziție (RON):", value=50000.0)
        durata_viata_luni = c3.number_input("Durată amortizare (luni):", value=36)
        
        ore_utilizare_luna = st.number_input("Ore utilizare pe lună:", value=100)
        
        if st.form_submit_button("➕ Adaugă Echipament"):
            cost_luna = valoare / durata_viata_luni if durata_viata_luni > 0 else 0
            cost_minut = cost_luna / (ore_utilizare_luna * 60) if ore_utilizare_luna > 0 else 0
            st.session_state.echipamente.append({
                "Nume": nume_eq, "Investiție": valoare, "Cost/Minut": round(cost_minut, 4)
            })
            
    if st.session_state.echipamente:
        st.dataframe(pd.DataFrame(st.session_state.echipamente), use_container_width=True)
        
    st.button("Salvează și treci la Etapa 5 ➡️", on_click=set_step, args=(5,), type="primary")

# ==========================================
# ETAPA 5: CALCULATOR SERVICIU (DEVIZ PRO)
# ==========================================
elif st.session_state.step == 5:
    st.header("Etapa 5: Deviz & Inginerie Preț (Gross-Up)")
    
    if not st.session_state.tehnicieni or not st.session_state.camere:
        st.warning("⚠️ Adaugă cel puțin un Tehnician (Etapa 2) și un Spațiu de Lucru (Etapa 3) pentru a genera devize!")
    else:
        c1, c2 = st.columns(2)
        with c1:
            nume_srv = st.text_input("Nume Procedură (Serviciu):")
            
            optiuni_camere = {c['Nume']: c for c in st.session_state.camere}
            cam_sel = st.selectbox("Se execută în Spațiul:", list(optiuni_camere.keys()))
            
            optiuni_tech = {t['Nume']: t for t in st.session_state.tehnicieni}
            tech_sel = st.selectbox("Executat de (Profil Tehnician):", list(optiuni_tech.keys()))
            
            optiuni_eq = {e['Nume']: e for e in st.session_state.echipamente}
            eq_sel = st.selectbox("Aparat folosit (Opțional):", ["Niciun aparat"] + list(optiuni_eq.keys()))
            
            durata = st.number_input("Timp execuție (minute):", min_value=5, value=60)
            
        with c2:
            cost_mat = st.number_input("Cost materiale (rețetar brut - RON):", value=45.0)
            if st.checkbox("Aplică 7% marjă de siguranță materiale", value=True):
                cost_mat *= 1.07
                
            comision = st.number_input("Comision extra tehnician (% din Net):", value=15.0)
            marja_profit = st.number_input("Profit NET Afacere dorit (% din Net):", value=35.0)
            st.markdown('<div class="explaining-note"><b>ℹ️ Reverse Engineering:</b> Stabilim exact cu ce vrem să rămânem (ex: 35%), iar algoritmul calculează prețul final care să absoarbă toate taxele și cheltuielile fixate.</div>', unsafe_allow_html=True)

        # CALCULE
        camera = optiuni_camere[cam_sel]
        tehnician = optiuni_tech[tech_sel]
        cost_eq_min = optiuni_eq[eq_sel]['Cost/Minut'] if eq_sel != "Niciun aparat" else 0.0
        
        cost_regie = camera['Cost/Minut'] * durata
        cost_ineficienta = camera['Cost Ineficienta/Minut'] * durata # Partea din regie care e "stationare"
        cost_manopera_fixa = tehnician['Cost/Minut'] * durata
        cost_amortizare = cost_eq_min * durata
        
        cost_baza = cost_regie + cost_manopera_fixa + cost_amortizare + cost_mat
        
        # Algoritm Gross-Up
        numitor = 1.0 - (comision/100.0) - (marja_profit/100.0)
        if numitor <= 0:
            st.error("Procentele de comision și profit cumulate depășesc 100%! Prețul nu poate fi calculat.")
            pret_fara_tva = 0
        else:
            pret_fara_tva = cost_baza / numitor
            
        val_comision = pret_fara_tva * (comision/100.0)
        val_profit = pret_fara_tva * (marja_profit/100.0)
        
        # Taxe stat pe afacere
        forma = st.session_state.fiscal['forma']
        taxa_stat = (pret_fara_tva * 0.01) if "1%" in forma else (pret_fara_tva * 0.03) if "3%" in forma else (val_profit * 0.16) if "16%" in forma else (val_profit * 0.10)
        
        pret_final = (pret_fara_tva * 1.19) if st.session_state.fiscal['tva'] == "Plătitor (19%)" else pret_fara_tva

        if pret_fara_tva > 0:
            st.markdown("### 📊 Deviz Desfășurat")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Manoperă Totală", f"{(cost_manopera_fixa + val_comision):.2f} RON", "CIM Fix + Comision")
            m2.metric("Regie Absorbită", f"{cost_regie:.2f} RON", f"Din care Staționare: {cost_ineficienta:.2f} RON", delta_color="inverse")
            m3.metric("Profit Net (Firma)", f"{val_profit:.2f} RON")
            m4.metric("Taxe estimate Stat", f"{taxa_stat:.2f} RON")
            
            st.success(f"💰 PREȚ RECOMANDAT LA RAFT: {pret_final:,.2f} RON")

            if st.button("📥 Validează și Adaugă în Catalog", type="primary"):
                st.session_state.catalog_servicii.append({
                    "Serviciu": nume_srv, "Profil Tech": tech_sel, "Spațiu": cam_sel, "Timp(min)": durata,
                    "Cost Mat.": round(cost_mat, 2), "Manoperă Totală": round(cost_manopera_fixa + val_comision, 2),
                    "Regie": round(cost_regie, 2), "Cost Staționare (Ascuns)": round(cost_ineficienta, 2),
                    "Profit Net": round(val_profit, 2), "Preț Raft": round(pret_final, 2)
                })
                st.balloons()
                
    st.button("Mergi la Catalog ➡️", on_click=set_step, args=(6,))

# ==========================================
# ETAPA 6: AUDIT ȘI CATALOG EXPORT
# ==========================================
elif st.session_state.step == 6:
    st.header("Etapa 6: Registrul de Export Financiar")
    
    if not st.session_state.catalog_servicii:
        st.warning("Nu există servicii auditate. Mergi la Etapa 5.")
    else:
        df = pd.DataFrame(st.session_state.catalog_servicii)
        st.dataframe(df, use_container_width=True)
        
        # Calcul Profitabilitate Mix
        profit_mediu = df['Profit Net'].mean()
        st.info(f"📈 **Profit Net Mediu per Procedură în meniul actual:** {profit_mediu:.2f} RON")
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Descarcă Catalogul (CSV/Excel)", data=csv, file_name="catalog_servicii_proiect2.csv", mime="text/csv", type="primary")
