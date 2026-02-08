def number_to_text_uz(n):
    """
    Converts a number to Uzbek text.
    Correctly handles 'bir yuz' vs 'yuz' context if needed, but standard is 'bir yuz' for 100? 
    Actually often 'yuz' is enough, but accounting uses full form.
    """
    if n == 0: return "nol"
    
    units = ["", "bir", "ikki", "uch", "to'rt", "besh", "olti", "yetti", "sakkiz", "to'qqiz"]
    tens = ["", "o'n", "yigirma", "o'ttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "to'qson"]
    # scales: index 0 is for <1000 so empty, index 1 is ming, 2 is million etc.
    scales = ["", "ming", "million", "milliard", "trillion"]
    
    parts = []
    
    # Split into 3-digit chunks
    n_str = str(int(n))
    # Pad to multiple of 3
    while len(n_str) % 3 != 0:
        n_str = "0" + n_str
        
    chunks = [n_str[i:i+3] for i in range(0, len(n_str), 3)]
    # Retrieve scale index (starts high)
    scale_idx = len(chunks) - 1
    
    for chunk in chunks:
        val = int(chunk)
        if val > 0:
            sub_parts = []
            h = val // 100
            t = (val % 100) // 10
            u = val % 10
            
            if h > 0:
                sub_parts.append(units[h])
                sub_parts.append("yuz")
            if t > 0:
                sub_parts.append(tens[t])
            if u > 0:
                sub_parts.append(units[u])
                
            chunk_text = " ".join(sub_parts)
            if scale_idx > 0:
                chunk_text += " " + scales[scale_idx]
            parts.append(chunk_text)
            
        scale_idx -= 1
        
    return " ".join(parts).strip()

import qrcode
import io
import base64

def generate_qr_code(data):
    """
    Generates a QR code base64 string for embedding in HTML.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

def cleaner(val):
    if not val:
        return 0
    if isinstance(val, (int, float)):
        return val
    return float(str(val).replace(" ", "").replace(",", "."))
