
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User, Group
from .models import ProcessedDocument
import os
import openpyxl
import zipfile

class WorkflowSystemTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Helper: Create Group
        self.operator_group, _ = Group.objects.get_or_create(name='Operator')
        self.moderator_group, _ = Group.objects.get_or_create(name='Moderator')
        self.director_group, _ = Group.objects.get_or_create(name='Director')
        
        # Create Users
        self.operator = User.objects.create_user(username='op', password='pass')
        self.operator.groups.add(self.operator_group)
        
        self.moderator = User.objects.create_user(username='mod', password='pass')
        self.moderator.groups.add(self.moderator_group)
        
        self.director = User.objects.create_user(username='dir', password='pass')
        self.director.groups.add(self.director_group)
        
        # excel file
        self.excel_path = 'workflow_test.xlsx'
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Anketa"
        ws['A1'] = "Workflow Data"
        wb.save(self.excel_path)
        with open(self.excel_path, 'rb') as f:
            self.file_content = f.read()

    def tearDown(self):
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)
            
    def test_full_workflow(self):
        # 1. Operator Upload
        self.client.login(username='op', password='pass')
        file = SimpleUploadedFile("wf.xlsx", self.file_content, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response = self.client.post(reverse('upload_document'), {
            'file': file,
            'doc_type_anketa': 'on',
            'include_qr': 'on'
        })
        self.assertEqual(response.status_code, 302) # Redirect to dashboard
        
        doc = ProcessedDocument.objects.last()
        self.assertEqual(doc.status, 'pending_moderator')
        self.assertEqual(doc.uploaded_by, self.operator)
        self.assertFalse(bool(doc.processed_file)) # No file yet
        
        # 2. Moderator Approve
        self.client.login(username='mod', password='pass')
        response = self.client.post(reverse('approve_document', args=[doc.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['new_state'], 'Direktor Kutilmoqda')
        
        doc.refresh_from_db()
        self.assertEqual(doc.status, 'pending_director')
        self.assertEqual(doc.moderator_approved_by, self.moderator)
        
        # 3. Director Approve
        self.client.login(username='dir', password='pass')
        response = self.client.post(reverse('approve_document', args=[doc.id]))
        self.assertEqual(response.status_code, 200)
        
        doc.refresh_from_db()
        self.assertEqual(doc.status, 'completed')
        self.assertEqual(doc.director_approved_by, self.director)
        self.assertTrue(bool(doc.processed_file)) # generated
        
        # Check ZIP content
        with zipfile.ZipFile(doc.processed_file.path, 'r') as zf:
            self.assertIn('Anketa.pdf', zf.namelist())

    def test_permission_denied(self):
        # Operator tries to approve
        doc = ProcessedDocument.objects.create(status='pending_moderator', original_file=SimpleUploadedFile("t.xlsx", b""))
        self.client.login(username='op', password='pass')
        
        response = self.client.post(reverse('approve_document', args=[doc.id]))
        self.assertEqual(response.status_code, 403)
