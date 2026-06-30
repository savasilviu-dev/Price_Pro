import streamlit as st
import pandas as pd
import json
import os

# ==========================================
# CONFIGURARE PAGINĂ & DESIGN ENTERPRISE
# ==========================================
st.set_page_config(page_title="Mentorul Financiar Pro", layout="wide", initial_sidebar_state="collapsed")

TERRACOTTA = "#B05244"
DB_FILE = "date_salon.json"

st.markdown(f"""
    <style>
    .stApp {{ background-color: #FAFAFA; color: #333333; }}
    .main-header {{ text-align: center; color: {TERRACOTTA}; font-weight: 700; font-size: 2.6rem; margin-bottom: 0px; padding-bottom: 0px; }}
    .sub-header {{ text-align: center; font-style: italic; color: #666666; font-size: 1.1rem; margin-top: 5px; margin-bottom: 30px; }}
    .stTabs [data-baseweb="tab-list"] {{ background-color: transparent; border-bottom: 1px solid #E0E0E0; gap: 15px; }}
    .stTabs [data-baseweb="tab"] {{ color: #666666; font-weight: 600; font-size: 1rem; padding: 10px 5px; border: none; background-color: transparent; outline: none; }}
    .stTabs [aria-selected="true"] {{ color: {TERRACOTTA} !important; border-bottom: 3px solid {TERRACOTTA} !important; }}
    .elegant-box {{ background-color: #FFFFFF; border-left: 4px solid {TERRACOTTA}; padding: 15px 20px; border-radius: 4px; box-shadow: 0px 2px 6px rgba(0,0,0,0.04); margin-bottom: 20px; font-size: 0.95rem; }}
    .alert-box {{ background-color: #FFF2F2; border-left: 4px solid #D32F2F; padding: 15px 20px; border-radius: 4px; margin-bottom: 20px; color: #D32F2F; font-weight: bold; }}
    .success-box {{ background-color: #F0FFF4; border-left: 4px solid #38A169; padding: 15px 20px; border-radius: 4px; margin-bottom: 20px; color: #276749; font-weight: bold; }}
    .salon-map-container {{ display: flex; flex-wrap: wrap; gap: 15px; margin-top: 25px; margin-bottom: 25px; }}
    .room-visual-block {{ color: #333333; padding: 20px; border-radius: 6px; box-shadow: inset 0 0 0 1px rgba(0,0,0,0.05), 0px 4px 10px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }}
    .room-name-label {{ font-weight: 700; font-size: 1.1rem; margin-bottom: 5px; }}
    .room-size-label {{ font-size: 0.9rem; opacity: 0.85; font-weight: 500; }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Mentorul Financiar pentru Saloane</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Sistem Integrat de Audit, Configurare B2B pe MP și Gestiune Profit</p>', unsafe_allow_html=True)

# ==========================================
# MOTOR DE MEMORIE PERMANENTĂ (AUTO-SAVE)
# ==========================================
# 1. Încărcarea datelor la deschiderea/refresh-ul paginii
if 'initializat' not in st.session_state:
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                date_salvate = json.load(f)
            for key, value in date_salvate.items():
                st.session_state[key] = value
        except:
            pass
    st.session_state['initializat'] = True

# 2. Definire structuri lipsă (dacă e prima rulare vreodată)
if 'fiscal' not in st.session_state: 
    st.session_state.fiscal = {
        'div': 16.0, 'imp': 1.0, 'tva': 19.0, 'regim_tva': 'Neplătitor', 
        'suprafata_totala': 0.0, 'cost_baza_mp': 0.0, 'cost_receptie': 0.0, 
        'cost_marketing': 0.0, 'cost_protocol': 0.0, 'total_regie': 0.0,
        'zile_luna': 24, 'ore_zi': 8, 'grad_ocupare': 65
    }
if 'spatii' not in st.session_state: st.session_state.spatii = []
if 'echipa' not in st.session_state: st.session_state.echipa = []
if 'inventar' not in st.session_state: st.session_state.inventar = []
if 'produse' not in st.session_state: st.session_state.produse = []
if 'catalog' not in st.session_state: st.session_state.catalog = []

tabs = st.tabs(["1. Fiscalitate", "2. Structură Spații", "3. Regie & Timp Mort", "4. CAPEX (Inventar)", "5. Bază Date Produse", "6. Deviz (Rețetar)", "7. Oferte & Pachete"])

# ------------------------------------------
# TAB 1: FISCALITATE
# ------------------------------------------
with tabs[0]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Configurări Macro-Fiscalitate</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        regim_tva = st.radio("Regim TVA Salon:", ["Neplătitor", "Plătitor (Adaugă TVA la raft)"], horizontal=True)
        st.session_state.fiscal['tva'] = st.number_input("Cota TVA curentă (%):", value=st.session_state.fiscal.get('tva', 19.0)) if "Plătitor" in regim_tva else 0.0
        st.session_state.fiscal['regim_tva'] = regim_tva
        st.session_state.fiscal['imp'] = st.number_input("Impozit Firmă (Venit/Profit %):", value=st.session_state.fiscal.get('imp', 1.0))
        st.session_state.fiscal['div'] = st.number_input("Impozit Dividende în vigoare (%):", value=st.session_state.fiscal.get('div', 16.0))
        
    with c2:
        venit_net = st.number_input("Venit NET lunar țintă ca Administrator (RON):", value=10000.0, step=1000.0)
        salariu_minim = 3700.0
        venit_anual = venit_net * 12
        
        plafon, datorie_cass = 0, 0
        if venit_anual >= salariu_minim * 24: plafon, datorie_cass = 24, salariu_minim * 24 * 0.10
        elif venit_anual >= salariu_minim * 12: plafon, datorie_cass = 12, salariu_minim * 12 * 0.10
        elif venit_anual >= salariu_minim * 6: plafon, datorie_cass = 6, salariu_minim * 6 * 0.10
        
        st.markdown(f"""
        <div class="elegant-box">
            <b>Overview Fiscal Personal (CASS pe Dividende):</b><br>
            Pe baza țintei tale, extragerea anuală este de {venit_anual:,.2f} RON (Plafon de {plafon} salarii).<br>
            Taxa personală anuală estimată de plată: <b>{datorie_cass:,.2f} RON / an</b>.<br>
            <i>Notă strategică: Acest cost este reținut separat din dividende și nu se include în costul per minut al serviciilor din salon.</i>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 2: STRUCTURĂ SPAȚII (MP) & HARTA VIZUALĂ
# ------------------------------------------
with tabs[1]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Definire Compartimentare Afacere (Metri Pătrați)</h3>", unsafe_allow_html=True)
    
    with st.container():
        s1, s2 = st.columns(2)
        nume_spatiu = s1.text_input("Denumire Cameră / Cabinet (ex: Cabinet Laser, Post Coafură 1):")
        suprafata_spatiu = s2.number_input("Suprafață Utilă Alocată (mp):", min_value=1.0, value=15.0, step=1.0)
        
        if st.button("Înregistrează Cabinet"):
            if nume_spatiu:
                st.session_state.spatii.append({"Spațiu": nume_spatiu, "Suprafață (mp)": suprafata_spatiu})
            
    if st.session_state.spatii:
        df_spatii = pd.DataFrame(st.session_state.spatii)
        st.dataframe(df_spatii, use_container_width=True)
        
        suprafata_utila_totala = df_spatii["Suprafață (mp)"].sum()
        st.session_state.fiscal['suprafata_totala'] = suprafata_utila_totala
        
        st.markdown(f"#### 🗺️ Hartă Financiar-Spațială a Salonului (Suprafață Totală: {suprafata_utila_totala:.2f} mp)")
        
        PREMIUM_PALETTE = ["#E6CCB2", "#DDB892", "#B7B7A4", "#A5A58D", "#CB997E", "#DDA15E", "#9A8C98", "#C7CCB9", "#D8C3A5", "#EAE7DC"]
        map_html = '<div class="salon-map-container">'
        for idx, row in df_spatii.iterrows():
            culoare = PREMIUM_PALETTE[idx % len(PREMIUM_PALETTE)]
            flex_basis = int(row["Suprafață (mp)"]) * 12
            map_html += f'<div class="room-visual-block" style="background-color: {culoare}; flex: 1 1 {flex_basis}px; min-height: 120px;"><span class="room-name-label">{row["Spațiu"]}</span><span class="room-size-label">{row["Suprafață (mp)"]} mp</span></div>'
        map_html += '</div>'
        st.markdown(map_html, unsafe_allow_html=True)

# ------------------------------------------
# TAB 3: REGIE, TIMP MORT & SUBÎNCHIRIERE B2B
# ------------------------------------------
with tabs[2]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Centru Costuri Fixe & Management Timp Mort</h3>", unsafe_allow_html=True)
    
    if st.session_state.fiscal['suprafata_totala'] == 0:
        st.warning("Vă rugăm să definiți mai întâi spațiile în Tab-ul 2.")
    else:
        st.markdown("#### 1. Parametri de Funcționare (Penalizare Timp Mort)")
        t1, t2, t3 = st.columns(3)
        st.session_state.fiscal['zile_luna'] = t1.number_input("Zile deschise / lună:", min_value=1, value=st.session_state.fiscal.get('zile_luna', 24))
        st.session_state.fiscal['ore_zi'] = t2.number_input("Ore active / zi:", min_value=1, value=st.session_state.fiscal.get('ore_zi', 10))
        st.session_state.fiscal['grad_ocupare'] = t3.slider("Grad Mediu de Ocupare (%) - Absoarbe timpul gol:", 10, 100, st.session_state.fiscal.get('grad_ocupare', 65))

        st.markdown("#### 2. Cheltuieli Globale Salon")
        r1, r2, r3 = st.columns(3)
        chirie_bruta = r1.number_input("Chirie Brută Imobil (RON/lună):", value=8000.0)
        utilitati = r1.number_input("Utilități & Curățenie (RON/lună):", value=2500.0)
        contabilitate = r1.number_input("Contabilitate & Soft Gestiune (RON/lună):", value=1500.0)
        
        st.session_state.fiscal['cost_marketing'] = r2.number_input("Marketing Global (Meta Ads, Content):", value=st.session_state.fiscal.get('cost_marketing', 3000.0))
        st.session_state.fiscal['cost_protocol'] = r2.number_input("Protocol Global (Cafea, Apă):", value=st.session_state.fiscal.get('cost_protocol', 1000.0))
        
        are_receptie = r3.checkbox("Recepție dedicată?", value=True)
        st.session_state.fiscal['cost_receptie'] = r3.number_input("Salariu + Taxe Recepție (RON/lună):", value=st.session_state.fiscal.get('cost_receptie', 4500.0)) if are_receptie else 0.0
        
        st.session_state.fiscal['total_regie'] = chirie_bruta + utilitati + contabilitate + st.session_state.fiscal['cost_marketing'] + st.session_state.fiscal['cost_protocol'] + st.session_state.fiscal['cost_receptie']
        cost_infrastructura_luna = chirie_bruta + utilitati + contabilitate
        st.session_state.fiscal['cost_baza_mp'] = cost_infrastructura_luna / st.session_state.fiscal['suprafata_totala']
        
        st.markdown("---")
        st.markdown("#### 📐 Simulator Imobiliar Comercial B2B (Rent-a-chair pe MP)")
        
        spatii_disponibile = [s["Spațiu"] for s in st.session_state.spatii]
        camera_aleasa = st.selectbox("Selectați Camera destinată subînchirierii:", spatii_disponibile)
        space_info = next(s for s in st.session_state.spatii if s["Spațiu"] == camera_aleasa)
        suprafata_camera = space_info["Suprafață (mp)"]
        
        inc_receptie = st.checkbox("Include acces la Recepție și Soft")
        inc_marketing = st.checkbox("Include cota-parte din Marketingul Global")
        inc_protocol = st.checkbox("Include Facilități Protocol")
        
        cota_rec_mp = (st.session_state.fiscal['cost_receptie'] / st.session_state.fiscal['suprafata_totala']) if inc_receptie else 0.0
        cota_mkt_mp = (st.session_state.fiscal['cost_marketing'] / st.session_state.fiscal['suprafata_totala']) if inc_marketing else 0.0
        cota_prt_mp = (st.session_state.fiscal['cost_protocol'] / st.session_state.fiscal['suprafata_totala']) if inc_protocol else 0.0
        
        amortizare_camera_specifica = sum(i["Amortizare/Lună (RON)"] for i in st.session_state.inventar if i.get("Spațiu Arondat") == camera_aleasa) if st.session_state.inventar else 0.0
        
        pret_minim_mp_camera = st.session_state.fiscal['cost_baza_mp'] + cota_rec_mp + cota_mkt_mp + cota_prt_mp
        cost_total_camera = pret_minim_mp_camera * suprafata_camera
        cost_total_break_even_camera = cost_total_camera + amortizare_camera_specifica
        
        st.markdown(f"""
        <div class="elegant-box">
            <b>Break-Even Subînchiriere Cameră ({suprafata_camera} mp):</b><br>
            • Cost Bază Infrastructură: {cost_total_camera:.2f} RON/lună ({pret_minim_mp_camera:.2f} RON/mp)<br>
            • Amortizare Echipamente/Mobilier (3 ani): {amortizare_camera_specifica:.2f} RON/lună<br>
            🎯 <b>PRAG RENTABILITATE CAMERA COMPLETĂ (Full-Time): {cost_total_break_even_camera:.2f} RON / lună</b><br>
            🌗 <b>PRAG RENTABILITATE JUMĂTATE DE TURĂ: {cost_total_break_even_camera / 2:.2f} RON / lună</b>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------
# TAB 4: CAPEX (INVENTAR CONFIGURAT LA 3 ANI)
# ------------------------------------------
with tabs[3]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Registru Mijloace Mobile: Amortizare la 3 ani</h3>", unsafe_allow_html=True)
    
    if not st.session_state.spatii:
        st.warning("Definiți mai întâi spațiile în Tab-ul 2.")
    else:
        with st.container():
            c1, c2, c3 = st.columns(3)
            n_item = c1.text_input("Denumire Bun (Scaun, Pat, Laser):")
            v_item = c2.number_input("Valoare Achiziție Factură (RON):", min_value=0.0, value=7200.0)
            room_assigned = c3.selectbox("Arondează la Spațiul/Camera:", [s["Spațiu"] for s in st.session_state.spatii])
            
            if st.button("Înregistrează Active"):
                amortizare_luna = v_item / 36
                st.session_state.inventar.append({
                    "Denumire": n_item, "Valoare (RON)": v_item,
                    "Amortizare/Lună (RON)": round(amortizare_luna, 2), "Spațiu Arondat": room_assigned
                })
                
        if st.session_state.inventar: 
            st.dataframe(pd.DataFrame(st.session_state.inventar), use_container_width=True)
            if st.button("🧹 Șterge tot inventarul"):
                st.session_state.inventar = []
                st.rerun()

# ------------------------------------------
# TAB 5: BAZĂ DATE PRODUSE
# ------------------------------------------
with tabs[4]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Inventar Materiale & Stoc Backbar</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    n_prod = c1.text_input("Nume Consumabil (ex: Vopsea Tub 100ml):")
    p_lot = c2.number_input("Cost Achiziție Lot (RON):", value=60.0)
    cant = c3.number_input("Număr total unități/ml:", value=100.0)
    
    if st.button("Salvează în stoc"):
        pret_unitar = p_lot / cant if cant > 0 else 0
        st.session_state.produse.append({"Produs": n_prod, "Preț/UM (RON)": round(pret_unitar, 4)})
        
    if st.session_state.produse: 
        st.dataframe(pd.DataFrame(st.session_state.produse), use_container_width=True)
        if st.button("🧹 Șterge toate produsele"):
            st.session_state.produse = []
            st.rerun()

# ------------------------------------------
# TAB 6: DEVIZ (REȚETAR)
# ------------------------------------------
with tabs[5]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Calculator Deviz Financiar Ușă-în-Ușă</h3>", unsafe_allow_html=True)
    
    if not st.session_state.spatii or st.session_state.fiscal['total_regie'] == 0:
        st.warning("Configurați Spațiile și Regia pentru a accesa calculatorul.")
    else:
        nume_serv = st.text_input("Nume Procedură:")
        
        col_t1, col_t2 = st.columns(2)
        t_efectiv = col_t1.number_input("Timp efectiv de lucru (minute):", value=45)
        t_camera = col_t2.number_input("Timp total blocare cameră Ușă-în-Ușă (minute):", value=65)
        
        st.markdown("**Resurse Umane & Spațiu:**")
        st.session_state.echipa = [{"Nume": "Angajat CIM", "Tip": "CIM", "Cost_Min": 0.5}, {"Nume": "Colaborator PFA B2B", "Tip": "B2B", "Procent": 30.0}]
        tech_selectat = st.selectbox("Alege cine execută procedura:", [t["Nume"] for t in st.session_state.echipa])
        room_selected = st.selectbox("Se execută în Camera:", [s["Spațiu"] for s in st.session_state.spatii])
        
        st.markdown("**Rețetar Materiale:**")
        materiale_alese = st.multiselect("Selectează consumabile:", [p["Produs"] for p in st.session_state.produse])
        
        cost_mat_brut = 0.0
        for m_name in materiale_alese:
            p_inf = next(p for p in st.session_state.produse if p["Produs"] == m_name)
            qty = st.number_input(f"Cantitate {m_name}:", value=1.0)
            cost_mat_brut += qty * p_inf["Preț/UM (RON)"]
            
        bifa_risipa = st.checkbox("Aplică marjă risipă (+10%)", value=True)
        cost_mat_final = cost_mat_brut * 1.10 if bifa_risipa else cost_mat_brut
        
        st.markdown("---")
        pret_simulat_net = st.number_input("💰 Preț propus de vânzare (fără TVA) - RON:", value=250.0)
        
        if st.button("Evaluează Structura de Preț"):
            minute_productive_luna = st.session_state.fiscal['zile_luna'] * st.session_state.fiscal['ore_zi'] * 60 * (st.session_state.fiscal['grad_ocupare'] / 100.0)
            
            suprafata_camerei = next(s["Suprafață (mp)"] for s in st.session_state.spatii if s["Spațiu"] == room_selected)
            pondere_camera = suprafata_camerei / st.session_state.fiscal['suprafata_totala']
            
            cost_regie_luna_camera = st.session_state.fiscal['total_regie'] * pondere_camera
            cost_regie_minut = cost_regie_luna_camera / minute_productive_luna if minute_productive_luna > 0 else 0
            cost_regie_absorbita = t_camera * cost_regie_minut
            
            c_uzura_luna = sum(i["Amortizare/Lună (RON)"] for i in st.session_state.inventar if i.get("Spațiu Arondat") == room_selected)
            cost_uzura_minut = c_uzura_luna / minute_productive_luna if minute_productive_luna > 0 else 0
            cost_capex_absorbit = t_efectiv * cost_uzura_minut
            
            cost_infrastructura = cost_regie_absorbita + cost_capex_absorbit + cost_mat_final
            tech_info = next(t for t in st.session_state.echipa if t["Nume"] == tech_selectat)
            
            if tech_info["Tip"] == "CIM":
                cost_manopera_fixa = t_efectiv * tech_info.get("Cost_Min", 0)
                break_even = cost_infrastructura + cost_manopera_fixa
                profit_operational = pret_simulat_net - break_even
                plata_tehnician = cost_manopera_fixa
            else: 
                break_even = cost_infrastructura
                profit_brut_pre_colaborare = pret_simulat_net - break_even
                
                if profit_brut_pre_colaborare > 0:
                    plata_tehnician = profit_brut_pre_colaborare * (tech_info.get("Procent", 30) / 100.0)
                    profit_operational = profit_brut_pre_colaborare - plata_tehnician
                else:
                    plata_tehnician = 0
                    profit_operational = profit_brut_pre_colaborare
            
            taxa_firma = profit_operational * (st.session_state.fiscal['imp'] / 100.0) if profit_operational > 0 else 0
            profit_net_firma = profit_operational - taxa_firma if profit_operational > 0 else profit_operational
            pret_final_client = pret_simulat_net * (1 + st.session_state.fiscal['tva'] / 100.0)
            
            if pret_simulat_net < break_even:
                st.markdown(f'<div class="alert-box">⚠️ ALERTĂ: Prețul de {pret_simulat_net} RON este sub Break-Even-ul de {break_even:.2f} RON! Afacerea pierde bani.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box">✅ FINANCIAR STABIL: Break-even acoperit ({break_even:.2f} RON). Preț cu TVA la raft: {pret_final_client:.2f} RON.</div>', unsafe_allow_html=True)
                
            st.write(f"• Regie Cameră Absorbită (penalizare timp mort inclusă): {cost_regie_absorbita:.2f} RON")
            st.write(f"• Consumabile (marjă inclusă): {cost_mat_final:.2f} RON")
            st.write(f"• Amortizare Echipamente (Timp efectiv): {cost_capex_absorbit:.2f} RON")
            st.write(f"• **Remunerație Tehnician ({tech_info['Tip']}): {plata_tehnician:.2f} RON**")
            st.write(f"💎 **PROFIT NET SALON CONSOLIDAT: {profit_net_firma:.2f} RON**")
            
            st.session_state.catalog.append({"Nume": nume_serv, "Preț Bază": pret_simulat_net, "Break-Even": round(break_even, 2), "Profit Net": round(profit_net_firma, 2)})

        if st.session_state.catalog:
            st.markdown("#### Baza de Date Servicii (Catalog)")
            st.dataframe(pd.DataFrame(st.session_state.catalog), use_container_width=True)
            if st.button("🧹 Șterge tot catalogul"):
                st.session_state.catalog = []
                st.rerun()

# ------------------------------------------
# TAB 7: OFERTE & PACHETE
# ------------------------------------------
with tabs[6]:
    st.markdown(f"<h3 style='color: {TERRACOTTA};'>Gaură Cash-Flow vs Pachete Profitabile</h3>", unsafe_allow_html=True)
    
    if not st.session_state.catalog:
        st.warning("Introduceți și validați servicii în Tab-ul 6 pentru a crea oferte.")
    else:
        nume_pachet = st.text_input("Denumire Promoție:")
        alese_pachet = st.multiselect("Adaugă proceduri în pachet:", [c["Nume"] for c in st.session_state.catalog])
        
        be_pachet_total, pret_intreg_total = 0.0, 0.0
        for s_name in alese_pachet:
            c_info = next(c for c in st.session_state.catalog if c["Nume"] == s_name)
            nr_sedinte = st.number_input(f"Ședințe de {s_name}:", min_value=1, value=1)
            be_pachet_total += c_info["Break-Even"] * nr_sedinte
            pret_intreg_total += c_info["Preț Bază"] * nr_sedinte
            
        st.write(f"Preț de listă (achiziție individuală): **{pret_intreg_total:.2f} RON**")
        st.write(f"🛡️ Cost de Producție (Break-Even Real): **{be_pachet_total:.2f} RON**")
        pret_oferta = st.number_input("Setează prețul promoțional (RON):", value=pret_intreg_total)
        
        if st.button("Validează Oferta"):
            if pret_oferta < be_pachet_total:
                st.markdown(f'<div class="alert-box">🛑 STRATEGIE TOXICĂ! Pierzi {- (pret_oferta - be_pachet_total):.2f} RON la fiecare pachet vândut.</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box">💎 PROMOȚIE SIGURĂ: Profit curat estimat de {pret_oferta - be_pachet_total:.2f} RON / pachet.</div>', unsafe_allow_html=True)

# ==========================================
# EXECUTARE SALVARE AUTOMATĂ
# ==========================================
date_export = {
    'fiscal': st.session_state.fiscal,
    'spatii': st.session_state.spatii,
    'echipa': st.session_state.echipa,
    'inventar': st.session_state.inventar,
    'produse': st.session_state.produse,
    'catalog': st.session_state.catalog
}
try:
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(date_export, f, ensure_ascii=False, indent=4)
except Exception:
    pass
