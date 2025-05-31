from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=True)

class MedicalProfileForm(forms.Form):
    age = forms.IntegerField(required=False)
    blood_group = forms.ChoiceField(
        choices=[
            ('', 'Select Blood Group'),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ],
        required=False
    )
    height = forms.FloatField(required=False)
    weight = forms.FloatField(required=False)
    allergies = forms.CharField(widget=forms.Textarea, required=False)
    chronic_conditions = forms.CharField(widget=forms.Textarea, required=False)
    current_medications = forms.CharField(widget=forms.Textarea, required=False)
    previous_surgeries = forms.CharField(widget=forms.Textarea, required=False)
