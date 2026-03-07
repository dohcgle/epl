import os

filepath = '/home/ulugbek/Projects/epl/templates/document_processor/loan_edit.html'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The extra_js block starts at line 1226 (index 1225)
# We want to replace from line 1229 (index 1228) to line 1394 (index 1393)

new_js = """    const { createApp, ref, reactive, computed, onMounted, watch } = Vue;

    const app = createApp({
        setup() {
            const currentStep = ref(1);
            const kinshipChoices = [
                { value: 'turmush_ortogi', label: "Turmush o'rtog'i" },
                { value: 'ota', label: 'Ota' },
                { value: 'ona', label: 'Ona' },
                { value: 'aka', label: 'Aka' },
                { value: 'uka', label: 'Uka' },
                { value: 'opa', label: 'Opa' },
                { value: 'singil', label: 'Singil' }
            ];
            const loanTypeChoices = [
                { value: 'mikroqarz', label: 'Mikroqarz' },
                { value: 'iste_mol', label: "Iste'mol krediti" },
                { value: 'avtokredit', label: 'Avtokredit' }
            ];
            const graphChoices = [
                { value: 'annuitet', label: 'Annuitet' },
                { value: 'differensial', label: 'Differensial' }
            ];
            const propertyTypeChoices = [
                { value: 'uy', label: 'Uy / Hovli' },
                { value: 'kvartira', label: 'Kvartira' },
                { value: 'dala_hovli', label: 'Dala hovli' },
                { value: 'noturar_joy', label: 'Noturar joy' }
            ];

            const personal = ref({ fish: '', fish_inisiali: '', pasport_seriya: '', jshshir: '', tugilgan_sana: '', jinsi: '', telefon: '', pasport_berilgan: '', manzil: '' });
            const contacts = ref([{ telefon: '', qarindoshlik: '' }, { telefon: '', qarindoshlik: '' }]);
            const loan = ref({ shartnoma_raqami: '', shartnoma_sanasi: '', boshlanish_sanasi: '', tugash_sanasi: '', miqdori: '', miqdori_soz: '', muddat_oy: '', muddat_oy_soz: '', foiz: '', foiz_soz: '', turi: 'mikroqarz', grafik: 'annuitet', grafik_matni: '' });
            const ownerType = ref('borrower');
            const selectedCollaterals = ref([]);
            const sugurtaMavjud = ref(false);
            const collateral = ref({
                owner_fish: '', owner_initials: '', owner_birth_date: '', owner_passport: '', owner_jshshir: '', owner_gender: '', owner_passport_given_by: '', owner_address: '',
                notarius_fish: '', notarius_address: '', reestr_number: '', reestr_date: '',
                avto_nomi: '', avto_kuzov_turi: '', avto_kuzov: '', avto_dvigatel: '', avto_shassi: '', avto_rang: '', avto_yil: null, avto_texpasport: '', avto_texpasport_sana: '', avto_manzil: '', avto_raqam: '', avto_bahosi: '', avto_bahosi_soz: '',
                mulk_turi: '', mulk_umumiy: '', mulk_qurilish: '', mulk_foydalanish: '', mulk_yashash: '', mulk_reestr_raqami: '', mulk_kadastr: '', mulk_manzil: '', mulk_bahosi: '', mulk_bahosi_soz: '',
                tilla_nomi: '', tilla_probi: '', tilla_vazni: '', tilla_soni: null, tilla_bahosi: '', tilla_bahosi_soz: '',
                sugurta_kompaniya: '', sugurta_polisi: '', sugurta_sana: '', sugurta_summa: '', sugurta_summa_soz: ''
            });

            const financial = ref({ ish_joyi: '', daromad: '', xarajatlar: '', tahminiy_tolov: '', majburiyatlar: '', filial_nomi: '', filial_boshligi: '', filial_boshligi_inisiali: '', tashkilot_nomi: '', direktor_fish: '', direktor_fish_inisiali: '' });

            const steps = [1, 2, 3, 4, 5];
            const stepTitles = ["Shaxsiy Ma'lumotlar", "Bog'lanish uchun shaxslar", "Kredit Ma'lumotlari & Grafik", "Garov Ta'minoti", "Moliyaviy Holat & Tashkilot"];

            const borrowerFish = computed(() => personal.value.fish);
            const borrowerInitials = computed(() => personal.value.fish_inisiali);

            const isStep1Valid = computed(() => {
                const p = personal.value;
                if (!p.fish || String(p.fish).trim() === '') return false;
                const jshStr = String(p.jshshir || '').replace(/\s/g, '').replace(/_/g, '');
                return jshStr.length === 14;
            });

            const isStep3Valid = computed(() => {
                const l = loan.value;
                const sNum = String(l.shartnoma_raqami || '').trim();
                const miqdor = String(l.miqdori || '').replace(/\s/g, '');
                return sNum !== '' && miqdor !== '' && miqdor !== '0';
            });

            const nextStep = () => { if (currentStep.value < 5) currentStep.value++; window.scrollTo({ top: 0, behavior: 'smooth' }); };
            const prevStep = () => { if (currentStep.value > 1) currentStep.value--; window.scrollTo({ top: 0, behavior: 'smooth' }); };
            const setOwnerType = (type) => { ownerType.value = type; };

            const showJsonPreview = () => {
                const fullData = { personal: personal.value, contacts: contacts.value, loan: loan.value, collateral: { ...collateral.value, selected_types: selectedCollaterals.value, owner_type: ownerType.value }, financial: financial.value };
                document.getElementById('jsonContent').textContent = JSON.stringify(fullData, null, 4);
                $('#jsonResultModal').modal('show');
            };

            const submitForm = async () => {
                let finalizedCollateral = { ...collateral.value };
                if (ownerType.value === 'borrower') {
                    finalizedCollateral.owner_fish = personal.value.fish;
                    finalizedCollateral.owner_initials = personal.value.fish_inisiali;
                    finalizedCollateral.owner_birth_date = personal.value.tugilgan_sana;
                    finalizedCollateral.owner_passport = personal.value.pasport_seriya;
                    finalizedCollateral.owner_jshshir = personal.value.jshshir;
                    finalizedCollateral.owner_gender = personal.value.jinsi;
                    finalizedCollateral.owner_passport_given_by = personal.value.pasport_berilgan;
                    finalizedCollateral.owner_address = personal.value.manzil;
                }
                const fullData = {
                    personal: personal.value,
                    contacts: contacts.value,
                    loan: loan.value,
                    collateral: { ...finalizedCollateral, selected_types: selectedCollaterals.value, owner_type: ownerType.value },
                    financial: financial.value,
                    sugurtaMavjud: selectedCollaterals.value.includes('sugurta')
                };
                try {
                    const res = await fetch(`/api/loans/update/{{ loan_id }}/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value },
                        body: JSON.stringify(fullData)
                    });
                    const data = await res.json();
                    if (res.ok && data.status === 'success') { alert("Muvaffaqiyatli saqlandi!"); window.location.href = '/documents/'; }
                    else { alert("Xatolik: " + (data.message || "Noma'lum")); }
                } catch (e) { alert("Tarmoq xatosi!"); }
            };

            const fillRandomStep = (step) => { /* Not implemented in edit */ };

            onMounted(() => {
                try {
                    const data = {{ loan_data_json|safe }};
                    if (data) {
                        if (data.personal) Object.assign(personal.value, data.personal);
                        if (data.contacts) contacts.value = (data.contacts.length >= 2) ? data.contacts : contacts.value;
                        if (data.loan) Object.assign(loan.value, data.loan);
                        if (data.financial) Object.assign(financial.value, data.financial);
                        if (data.collateral) {
                            ownerType.value = data.collateral.owner_type || 'borrower';
                            selectedCollaterals.value = data.collateral.selected_types || [];
                            Object.assign(collateral.value, data.collateral);
                        }
                    }
                } catch(e) { console.error("Data load error", e); }

                $('input:not([type="checkbox"]), select, textarea').addClass('form-control');
                $('.phone-mask').inputmask("+\\\\9\\\\98 99 999-99-99");
                $('.jshshir-mask').inputmask("99999999999999");
                $('.passport-mask').inputmask("AA9999999");
                $('.date-mask').inputmask("99.99.9999");
                $('.money-mask').inputmask({ alias: "numeric", groupSeparator: " ", autoGroup: true, digits: 0, rightAlign: false });

                $('input[data-model], select[data-model], textarea[data-model]').on('input keyup change', function () {
                    const val = $(this).val();
                    const modelPath = $(this).attr('data-model');
                    if (!modelPath) return;
                    const parts = modelPath.split('.');
                    if (parts.length === 2) {
                        const objName = parts[0];
                        const propName = parts[1];
                        if (objName.startsWith('contacts[')) {
                            const match = objName.match(/contacts\\[(\\d+)\\]/);
                            if (match) contacts.value[parseInt(match[1])][propName] = val;
                        } else {
                            if (objName === 'personal') personal.value[propName] = val;
                            if (objName === 'loan') loan.value[propName] = val;
                            if (objName === 'collateral') collateral.value[propName] = val;
                            if (objName === 'financial') financial.value[propName] = val;
                        }
                    }
                });
            });

            return {
                currentStep, ownerType, selectedCollaterals, sugurtaMavjud,
                personal, contacts, loan, collateral, financial,
                steps, stepTitles, kinshipChoices, loanTypeChoices, graphChoices, propertyTypeChoices,
                nextStep, prevStep, setOwnerType, submitForm, fillRandomStep, showJsonPreview,
                borrowerFish, borrowerInitials, isStep1Valid, isStep3Valid
            };
        },
        delimiters: ['[[', ']]']
    });
    app.mount('#app');
"""

# Find line 1229 (index 1228)
# We know it starts with 'const { createApp' or similar.

# Let's just find the first line in {% block extra_js %} that is NOT the script src tag.
start_idx = -1
for i, line in enumerate(lines):
    if '{% block extra_js %}' in line:
        # The next line is likely <script src=...
        # The one after that is likely <script>
        # So about 3 lines down.
        start_idx = i + 3
        break

# Find the line that has </script> and is near the end.
end_idx = -1
for i in range(len(lines)-1, -1, -1):
    if '</script>' in lines[i]:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_lines = lines[:start_idx] + [new_js + "\\n"] + lines[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("SUCCESS: extra_js updated correctly.")
else:
    print(f"ERROR: Indices not found. start_idx={start_idx}, end_idx={end_idx}")
