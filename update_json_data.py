import re
import json

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "r") as f:
    content = f.read()

# Eski json qaytarish form formati
old_return = """    form = UmumiyMalumotForm(initial=initial_data)
    
    return render(request, 'document_processor/process_audit.html', {
        'form': form,
        'edit_mode': True, 
        'loan': loan
    })"""
    
new_return = """    form = UmumiyMalumotForm(initial=initial_data)
    import json
    
    return render(request, 'document_processor/process_audit.html', {
        'form': form,
        'edit_mode': True, 
        'loan': loan,
        'loan_data_json': json.dumps(initial_data, ensure_ascii=False)
    })"""

content = content.replace(old_return, new_return)

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "w") as f:
    f.write(content)

with open("/home/ulugbek/Projects/epl/templates/document_processor/process_audit.html", "r") as f:
    html_content = f.read()

# JS ga ma'lumot yuborish
js_block = """
    {% if edit_mode %}
    // Edit qilinayotgan vaqtda barcha formalarni to'liq ochish 
    document.addEventListener('DOMContentLoaded', function () {
        setTimeout(function () {
            let readonlyInputs = document.querySelectorAll('input[readonly]');
            readonlyInputs.forEach(input => {
                input.removeAttribute('readonly');
                // Orqa fonni tozalash
                if (input.style.backgroundColor) {
                    input.style.backgroundColor = '';
                }
            });
            let disabledInputs = document.querySelectorAll('input[disabled], select[disabled], textarea[disabled]');
            disabledInputs.forEach(input => {
                input.removeAttribute('disabled');
            });
            
            // Xatolikka olib kelyotgan boshqa disable codlarni blokirovka qilindi JS da
        }, 1200);
        
        let loanData = {{ loan_data_json|safe }};
        if(loanData) {
            for (let key in loanData) {
                let el = document.getElementById('id_' + key);
                if (el && !el.value && loanData[key] != null) {
                    if (el.type === 'checkbox') {
                        el.checked = loanData[key];
                    } else if (el.tagName === 'SELECT') {
                        el.value = loanData[key];
                        // Select2 kabi pluginlar uchun trigger kerak bo'lishi mumkin
                        $(el).trigger('change');
                    } else {
                        el.value = loanData[key];
                    }
                }
            }
        }
        
    });
    {% endif %}"""

html_content = re.sub(r"\{\% if edit_mode \%}.*?\{\% endif \%\}", js_block, html_content, flags=re.DOTALL)

with open("/home/ulugbek/Projects/epl/templates/document_processor/process_audit.html", "w") as f:
    f.write(html_content)

print("json load added")
