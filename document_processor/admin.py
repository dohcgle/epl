from django.contrib import admin
from django.db import models
from .models import LoanWizardApplication, Profile
import json
from django.utils.safestring import mark_safe

@admin.register(LoanWizardApplication)
class LoanWizardApplicationAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'client_name', 'loan_amount', 'status', 
        'created_by', 'moderator_approved_by', 'director_approved_by',
        'json_actions', 'created_at'
    )
    search_fields = ('client_name',)
    list_filter = ('status', 'created_at', 'created_by')
    readonly_fields = (
        'created_by', 'created_at', 
        'moderator_approved_by', 'moderator_approved_at', 
        'director_approved_by', 'director_approved_at'
    )
    
    def json_actions(self, obj):
        if not obj.data:
            return "Bo'sh"
        json_str = json.dumps(obj.data, ensure_ascii=False)
        # Escaping for JS
        json_js_escaped = json_str.replace("'", "\\'").replace('"', '&quot;')
        
        return mark_safe(f"""
            <a href="data:text/json;charset=utf-8,{json_str}" download="app_{obj.id}.json" 
               style="padding: 3px 10px; background: #447e9b; color: white; border-radius: 4px; text-decoration: none; margin-right: 5px; font-size: 11px;">
               Yuklash
            </a>
            <button type="button" onclick='copyToClipboard("{json_js_escaped}")'
               style="padding: 3px 10px; background: #79aec8; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 11px;">
               Nusxa
            </button>
            <script>
                if (typeof copyToClipboard !== "function") {{
                    window.copyToClipboard = function(text) {{
                        const el = document.createElement("textarea");
                        el.value = text;
                        document.body.appendChild(el);
                        el.select();
                        document.execCommand("copy");
                        document.body.removeChild(el);
                        alert("JSON nusxalandi!");
                    }};
                }}
            </script>
        """)
    json_actions.short_description = 'JSON Amallar'



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'filial']
