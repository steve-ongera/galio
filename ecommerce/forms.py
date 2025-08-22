from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Address, User


class BillingAddressForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'required': True
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'required': True
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'required': True
        })
    )
    
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name'
        })
    )
    
    country = forms.CharField(
        max_length=100,
        widget=forms.Select(attrs={
            'class': 'form-control nice-select'
        }, choices=[
            ('', 'Select Country'),
            ('KE', 'Kenya'),
            ('UG', 'Uganda'),
            ('TZ', 'Tanzania'),
            ('RW', 'Rwanda'),
            ('BI', 'Burundi'),
            ('SS', 'South Sudan'),
            ('ET', 'Ethiopia'),
            ('SO', 'Somalia'),
            ('DJ', 'Djibouti'),
            ('ER', 'Eritrea'),
        ])
    )
    
    address_line_1 = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address Line 1',
            'required': True
        })
    )
    
    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address Line 2 (Optional)'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Town / City',
            'required': True
        })
    )
    
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State / Division'
        })
    )
    
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postcode / ZIP',
            'required': True
        })
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number'
        })
    )
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove any non-digit characters for validation
            digits_only = ''.join(filter(str.isdigit, phone))
            
            # Validate Kenyan phone numbers
            if len(digits_only) == 10 and digits_only.startswith('0'):
                return phone
            elif len(digits_only) == 9:
                return phone
            elif len(digits_only) == 12 and digits_only.startswith('254'):
                return phone
            else:
                raise forms.ValidationError('Please enter a valid phone number.')
        return phone


class ShippingAddressForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name',
            'required': True,
            'id': 'f_name_2'
        })
    )
    
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name',
            'required': True,
            'id': 'l_name_2'
        })
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address',
            'required': True,
            'id': 'email_2'
        })
    )
    
    company = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company Name',
            'id': 'com-name_2'
        })
    )
    
    country = forms.CharField(
        max_length=100,
        widget=forms.Select(attrs={
            'class': 'form-control nice-select',
            'id': 'country_2'
        }, choices=[
            ('', 'Select Country'),
            ('KE', 'Kenya'),
            ('UG', 'Uganda'),
            ('TZ', 'Tanzania'),
            ('RW', 'Rwanda'),
            ('BI', 'Burundi'),
            ('SS', 'South Sudan'),
            ('ET', 'Ethiopia'),
            ('SO', 'Somalia'),
            ('DJ', 'Djibouti'),
            ('ER', 'Eritrea'),
        ])
    )
    
    address_line_1 = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address Line 1',
            'required': True,
            'id': 'street-address_2'
        })
    )
    
    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Street address Line 2 (Optional)'
        })
    )
    
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Town / City',
            'required': True,
            'id': 'town_2'
        })
    )
    
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'State / Division',
            'id': 'state_2'
        })
    )
    
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Postcode / ZIP',
            'required': True,
            'id': 'postcode_2'
        })
    )


class CheckoutForm(forms.Form):
    # This can be used for additional checkout-specific fields
    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes about your order, e.g. special notes for delivery.',
            'id': 'ordernote'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('mpesa', 'M-Pesa'),
            ('cash', 'Cash on Delivery'),
            ('bank', 'Bank Transfer'),
            ('paypal', 'PayPal'),
        ],
        widget=forms.RadioSelect(attrs={
            'class': 'payment-method-radio'
        }),
        initial='mpesa'
    )
    
    terms_accepted = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'custom-control-input',
            'id': 'terms'
        })
    )


class CouponForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Your Coupon Code',
            'required': True
        })
    )


class GuestCheckoutForm(forms.Form):
    """Form for guest checkout without creating an account"""
    create_account = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'custom-control-input',
            'id': 'create_pwd'
        })
    )
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Account Password',
            'id': 'pwd'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        create_account = cleaned_data.get('create_account')
        password = cleaned_data.get('password')
        
        if create_account and not password:
            raise forms.ValidationError('Password is required when creating an account.')
        
        return cleaned_data


class AddressSelectionForm(forms.Form):
    """Form for selecting from existing user addresses"""
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user.is_authenticated:
            addresses = Address.objects.filter(user=user)
            choices = [('new', 'Add new address')]
            
            for address in addresses:
                choice_label = f"{address.first_name} {address.last_name}, {address.address_line_1}, {address.city}"
                choices.append((address.id, choice_label))
            
            self.fields['billing_address'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'address-selection'}),
                initial='new'
            )
            
            self.fields['shipping_address'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'address-selection'}),
                initial='new',
                required=False
            )


from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User, Address


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control-file'
            }),
        }


class AddressForm(forms.ModelForm):
    """Form for adding/editing addresses"""
    
    class Meta:
        model = Address
        fields = [
            'address_type', 'first_name', 'last_name', 'company',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'phone', 'is_default'
        ]
        widgets = {
            'address_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company (Optional)'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line 1'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Address Line 2 (Optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country',
                'value': 'Kenya'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ContactForm(forms.Form):
    """Contact us form"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your Message',
            'rows': 6
        })
    )