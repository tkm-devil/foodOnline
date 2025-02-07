from .models import User

def detectUser(user):
    if user.role == User.CUSTOMER:
        redirectUrl = 'customerDashboard'
        return redirectUrl
    elif user.role == User.VENDOR:
        redirectUrl = 'vendorDashboard'
        return redirectUrl
    elif user.role == None and user.is_superuser:
        redirectUrl = '/admin'
        return redirectUrl