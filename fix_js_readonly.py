import re

with open("/home/ulugbek/Projects/epl/templates/document_processor/process_audit.html", "r") as f:
    content = f.read()

# 1. muddat_soz_input ni html js da auto disabled/readonly qilish o'chirib tashlanadi
content = content.replace("$muddatSozInput.prop('readonly', true);", "")

# 2. barcha disabled checklarni olib tashlash
content = content.replace("$avtoFields.hide().find(':input').prop('disabled', true);", "$avtoFields.hide().find(':input').prop('disabled', false);")
content = content.replace("$kochmasFields.hide().find(':input').prop('disabled', true);", "$kochmasFields.hide().find(':input').prop('disabled', false);")
content = content.replace("$tillaFields.hide().find(':input').prop('disabled', true);", "$tillaFields.hide().find(':input').prop('disabled', false);")

content = content.replace("$sugurtaInputs.prop('disabled', true);", "$sugurtaInputs.prop('disabled', false);")
content = content.replace("$ownerInputs.prop('disabled', true);", "$ownerInputs.prop('disabled', false);")

# 3. form qismidagi "disabled" xususiyatiga ega inputlarni tozalash (o'z ehtiyoty yuzasidan)
new_js = """    {% if edit_mode %}
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
    });
    {% endif %}"""

content = re.sub(r"\{\% if edit_mode \%}.*?\{\% endif \%\}", new_js, content, flags=re.DOTALL)

with open("/home/ulugbek/Projects/epl/templates/document_processor/process_audit.html", "w") as f:
    f.write(content)

print("html js updated")
