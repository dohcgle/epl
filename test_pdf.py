from document_processor.models import LoanApplication
from document_processor.views import generate_loan_docs
import sys

# Loglarni alohida faylga yozamiz
with open("pdf_test_log.txt", "w") as f:
    class DummyRequest:
        def build_absolute_uri(self, location):
            return f"http://localhost:8000{location}"

    try:
        loan = LoanApplication.objects.last()
        if loan:
            f.write(f"Testing PDF generation for Loan ID: {loan.id}\n")
            print(f"Testing PDF generation for Loan ID: {loan.id}")
            generate_loan_docs(DummyRequest(), loan)
            f.write("Success! PDF and ZIP generated.\n")
            print("Success! PDF and ZIP generated.")
        else:
            f.write("Bazada xech qanday ariza topilmadi.\n")
    except Exception as e:
        import traceback
        f.write("ERROR:\n")
        f.write(traceback.format_exc() + "\n")
        print("ERROR OCCURRED, CHECK pdf_test_log.txt")
