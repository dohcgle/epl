import re

with open("/home/ulugbek/Projects/epl/templates/document_processor/loan_edit.html", "r") as f:
    content = f.read()

# Eski onMounted bloki
old_mounted = """            // DATA YUKLANISHI (ON MOUNTED)
            onMounted(async () => {
                try {
                    const res = await fetch(`/api/loans/{{ loan_id }}/`);
                    const data = await res.json();
                    if(data.status === 'success') {
                        // Personal
                        Object.assign(personal.value, data.personal);
                        
                        // Contacts
                        if(data.contacts && data.contacts.length >= 2) {
                            contacts.value = data.contacts;
                        }

                        // Loan
                        Object.assign(loan.value, data.loan);

                        // Financial
                        Object.assign(financial.value, data.financial);

                        // Collateral
                        if(data.collateral) {
                            ownerType.value = data.collateral.owner_type || 'borrower';
                            selectedCollaterals.value = data.collateral.selected_types || [];
                            Object.assign(collateral.value, data.collateral);
                        }
                    }
                } catch(e) {
                    console.error("Malumotni yuklashda xatolik", e);
                }
            });"""

# Yangi onMounted kontekst ma'lumoti orqali
new_mounted = """            // DATA YUKLANISHI (CONTEXT ORQALI)
            onMounted(() => {
                try {
                    // Django'dan kelgan JSON string array-objectni script o'zi qabul qilib oladi
                    const data = {{ loan_data_json|safe }};

                    if(data) {
                        // Personal
                        if (data.personal) Object.assign(personal.value, data.personal);
                        
                        // Contacts
                        if(data.contacts && data.contacts.length >= 2) {
                            contacts.value = data.contacts;
                        }

                        // Loan
                        if (data.loan) Object.assign(loan.value, data.loan);

                        // Financial
                        if (data.financial) Object.assign(financial.value, data.financial);

                        // Collateral
                        if(data.collateral) {
                            ownerType.value = data.collateral.owner_type || 'borrower';
                            selectedCollaterals.value = data.collateral.selected_types || [];
                            Object.assign(collateral.value, data.collateral);
                        }
                    }
                } catch(e) {
                    console.error("Context ma'lumoti json.loads dagi xatolik:", e);
                }
            });"""

content = content.replace(old_mounted, new_mounted)

with open("/home/ulugbek/Projects/epl/templates/document_processor/loan_edit.html", "w") as f:
    f.write(content)

print("loan_edit.html updated for context data passing.")
