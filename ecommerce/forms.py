from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Address, User, County, DeliveryArea


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
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678',
            'required': True
        }),
        help_text='Required for delivery coordination'
    )
    
    county = forms.ModelChoiceField(
        queryset=County.objects.filter(is_active=True),
        empty_label='Select County',
        widget=forms.Select(attrs={
            'class': 'form-control county-select',
            'required': True
        })
    )
    
    delivery_area = forms.ModelChoiceField(
        queryset=DeliveryArea.objects.none(),  # Will be populated dynamically
        empty_label="Select Delivery Area",
        widget=forms.Select(attrs={
            'class': 'form-control area-select',
            'required': True
        })
    )
    
    detailed_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Building name, floor, apartment number, landmarks...\nExample: ABC Apartments, 2nd Floor, House No. 5B, Near Shell Petrol Station',
            'required': True
        }),
        help_text='Please provide specific details to help our delivery team find you'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handle prefixed form data (billing-county instead of county)
        county_field_name = 'county'
        if self.prefix:
            county_field_name = f'{self.prefix}-county'
        
        # If form has data, populate areas for selected county
        if self.data and county_field_name in self.data:
            try:
                county_id = int(self.data.get(county_field_name))
                self.fields['delivery_area'].queryset = DeliveryArea.objects.filter(
                    county_id=county_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.initial.get('county'):
            self.fields['delivery_area'].queryset = DeliveryArea.objects.filter(
                county=self.initial['county'], is_active=True
            ).order_by('name')
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Clean and validate Kenyan phone numbers
            digits_only = ''.join(filter(str.isdigit, phone))
            
            if len(digits_only) == 10 and digits_only.startswith('0'):
                return phone
            elif len(digits_only) == 9:
                return '0' + digits_only
            elif len(digits_only) == 12 and digits_only.startswith('254'):
                return '0' + digits_only[3:]
            elif len(digits_only) == 13 and digits_only.startswith('+254'):
                return '0' + digits_only[4:]
            else:
                raise forms.ValidationError('Please enter a valid Kenyan phone number.')
        return phone

    def clean_delivery_area(self):
        delivery_area = self.cleaned_data.get('delivery_area')
        county = self.cleaned_data.get('county')
        
        if delivery_area and county:
            # Verify that the delivery area belongs to the selected county
            if delivery_area.county != county:
                raise forms.ValidationError("Invalid delivery area for selected county.")
        
        return delivery_area


class ShippingAddressForm(forms.Form):
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
    
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678',
            'required': True
        })
    )
    
    county = forms.ModelChoiceField(
        queryset=County.objects.filter(is_active=True),
        empty_label='Select County',
        widget=forms.Select(attrs={
            'class': 'form-control county-select',
            'required': True,
            'id': 'shipping_county'
        })
    )
    
    delivery_area = forms.ModelChoiceField(
        queryset=DeliveryArea.objects.none(),
        empty_label='Select Area',
        widget=forms.Select(attrs={
            'class': 'form-control area-select',
            'required': True,
            'id': 'shipping_area'
        })
    )
    
    detailed_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Building name, floor, apartment number, landmarks...',
            'required': True
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Handle prefixed form data (shipping-county instead of county)
        county_field_name = 'county'
        if self.prefix:
            county_field_name = f'{self.prefix}-county'
        
        # If form has data, populate areas for selected county
        if self.data and county_field_name in self.data:
            try:
                county_id = int(self.data.get(county_field_name))
                self.fields['delivery_area'].queryset = DeliveryArea.objects.filter(
                    county_id=county_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                pass
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Clean and validate Kenyan phone numbers
            digits_only = ''.join(filter(str.isdigit, phone))
            
            if len(digits_only) == 10 and digits_only.startswith('0'):
                return phone
            elif len(digits_only) == 9:
                return '0' + digits_only
            elif len(digits_only) == 12 and digits_only.startswith('254'):
                return '0' + digits_only[3:]
            elif len(digits_only) == 13 and digits_only.startswith('+254'):
                return '0' + digits_only[4:]
            else:
                raise forms.ValidationError('Please enter a valid Kenyan phone number.')
        return phone

    def clean_delivery_area(self):
        delivery_area = self.cleaned_data.get('delivery_area')
        county = self.cleaned_data.get('county')
        
        if delivery_area and county:
            # Verify that the delivery area belongs to the selected county
            if delivery_area.county != county:
                raise forms.ValidationError("Invalid delivery area for selected county.")
        
        return delivery_area


class AddressSelectionForm(forms.Form):
    """Form for selecting from existing user addresses"""
    def __init__(self, user, address_type='shipping', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if user.is_authenticated:
            addresses = Address.objects.filter(user=user, address_type=address_type)
            choices = [('new', 'Add new address')]
            
            for address in addresses:
                shipping_fee = f"(Shipping: KSh {address.shipping_fee})" if address_type == 'shipping' else ""
                choice_label = f"{address.first_name} {address.last_name} - {address.delivery_area.name}, {address.county.name} {shipping_fee}"
                choices.append((address.id, choice_label))
            
            self.fields['selected_address'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect(attrs={'class': 'address-selection'}),
                initial='new',
                required=True
            )


class GuestCheckoutForm(forms.Form):
    """Form for guest checkout without creating an account"""
    create_account = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'custom-control-input',
            'id': 'create_pwd'
        }),
        label='Create an account for faster checkout next time?'
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


class CheckoutForm(forms.Form):
    order_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special delivery instructions?',
            'id': 'ordernote'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=[
            ('mpesa', 'M-Pesa (Instant)'),
            ('cash', 'Cash on Delivery'),
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
        }),
        label='I have read and agree to the terms and conditions'
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
            'address_type', 'first_name', 'last_name', 
            'county', 'delivery_area', 'detailed_address', 'is_default'
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
            'county': forms.Select(attrs={
                'class': 'form-control county-select'
            }),
            'delivery_area': forms.Select(attrs={
                'class': 'form-control area-select'
            }),
            'detailed_address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Building name, floor, apartment number, landmarks...',
                'rows': 3
            }),
            'is_default': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set up county queryset
        self.fields['county'].queryset = County.objects.filter(is_active=True)
        
        # If form has data, populate areas for selected county
        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['delivery_area'].queryset = DeliveryArea.objects.filter(
                    county_id=county_id, is_active=True
                ).order_by('name')
            except (ValueError, TypeError):
                self.fields['delivery_area'].queryset = DeliveryArea.objects.none()
        elif self.instance.pk and self.instance.county:
            # If editing existing address
            self.fields['delivery_area'].queryset = DeliveryArea.objects.filter(
                county=self.instance.county, is_active=True
            ).order_by('name')
        else:
            self.fields['delivery_area'].queryset = DeliveryArea.objects.none()


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


class NewsletterForm(forms.Form):
    """Newsletter subscription form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Email Address',
            'required': True
        })
    )


class UserRegistrationForm(UserCreationForm):
    """Custom user registration form"""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    first_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone Number (Optional)'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        if commit:
            user.save()
        return user