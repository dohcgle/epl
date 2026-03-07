import re

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "r") as f:
    content = f.read()

# 1. Edit loan initial data da auto.yurgan olib tashlanadi yoki hasattr orqali olinadi
old_initial = """                    'avto_bahosi': auto.bahosi,
                    'avto_yurgan': auto.yurgan,
                    'avto_texpasport': auto.texpasport,"""
new_initial = """                    'avto_bahosi': auto.bahosi,
                    'avto_yurgan': getattr(auto, 'yurgan', ''),
                    'avto_texpasport': auto.texpasport,"""

content = content.replace(old_initial, new_initial)

# 2. Saqlash (POST) vaqtida
old_post = """                    auto.rang = request.POST.get('avto_rang')
                    auto.yurgan = request.POST.get('avto_yurgan')
                    auto.bahosi = clean_int(request.POST.get('avto_bahosi'))"""
new_post = """                    auto.rang = request.POST.get('avto_rang')
                    if hasattr(auto, 'yurgan'):
                        auto.yurgan = request.POST.get('avto_yurgan')
                    auto.bahosi = clean_int(request.POST.get('avto_bahosi'))"""

content = content.replace(old_post, new_post)

with open("/home/ulugbek/Projects/epl/document_processor/views.py", "w") as f:
    f.write(content)

print("success view fx")
