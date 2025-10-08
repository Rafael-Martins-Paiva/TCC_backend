import qrcode
from io import BytesIO
from django.http import HttpResponse

class QRCodeGenerator:
    def generate(self, data: str) -> bytes:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()

def qr_code_view(request, data):
    generator = QRCodeGenerator()
    img_data = generator.generate(str(data))
    return HttpResponse(img_data, content_type="image/png")
