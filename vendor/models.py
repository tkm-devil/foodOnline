from django.db import models
from accounts.models import User, UserProfile
from foodOnline_main import settings
from django.core.mail import send_mail

# ✅ Vendor Model
class Vendor(models.Model):
    """Represents a vendor who sells food items."""
    user = models.OneToOneField(User, related_name='vendor', on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name='vendor_profile', on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/licenses/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor'
        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendors'
        ordering = ['-created_at']

    def __str__(self):
        return self.vendor_name
    
    def save(self, *args, **kwargs):
        """Override save method to send verification email when vendor is verified."""
        if self.pk:
            old_instance = Vendor.objects.filter(pk=self.pk).first()
            if old_instance and not old_instance.is_verified and self.is_verified:
                self.send_verification_success_email()
        super().save(*args, **kwargs)

    def send_verification_success_email(self):
        """Send email to vendor upon successful verification."""
        subject = "Your Vendor Account is Now Verified!"
        message = (
            f"Hello {self.vendor_name},\n\n"
            "Great news! Your vendor account has been successfully verified. 🎉\n"
            "You can now start listing and selling your products on our platform.\n\n"
            "Best regards,\n"
            "FoodOnline Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.user.email], fail_silently=False)


# ✅ VendorMenuItem Model (Independent)
class VendorMenuItem(models.Model):
    """Stores menu items created by vendors."""
    vendor = models.ForeignKey(Vendor, related_name="vendor_menu", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Food item name
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="vendor_menu_items/", blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendor_menu_item"
        verbose_name = "Vendor Menu Item"
        verbose_name_plural = "Vendor Menu Items"
        unique_together = ("vendor", "name")  # Ensures a vendor can't have duplicate items

    def __str__(self):
        return f"{self.name} - {self.vendor.vendor_name} @ ₹{self.price}"


# ✅ Order Model
class Order(models.Model):
    """Represents a customer's order."""
    STATUS_CHOICES = [
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Processing')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.customer.username} - {self.status}"
    
    def save(self, *args, **kwargs):
        """Update vendor earnings when an order is completed."""
        super().save(*args, **kwargs)
        if self.status == 'Completed':
            vendors = self.order_items.values_list('vendor', flat=True).distinct()
            for vendor_id in vendors:
                vendor = Vendor.objects.get(id=vendor_id)
                vendor.earnings.update_earnings()


# ✅ OrderItem Model
class OrderItem(models.Model):
    """Links an order with the items and vendors involved."""
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, related_name="order_items", on_delete=models.CASCADE)
    menu_item = models.ForeignKey(VendorMenuItem, related_name="order_items", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=8, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_item"
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} from {self.vendor.vendor_name} @ ₹{self.price_at_order} each"


# ✅ Earnings Model
class Earnings(models.Model):
    """Tracks total earnings of a vendor from completed orders."""
    vendor = models.OneToOneField(Vendor, related_name="earnings", on_delete=models.CASCADE)
    total_earnings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    last_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_payment_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'earnings'
        verbose_name = 'Earnings'
        verbose_name_plural = 'Earnings'

    def __str__(self):
        return f"Earnings for {self.vendor.vendor_name}: ₹{self.total_earnings}"
    
    def update_earnings(self):
        """Recalculate vendor earnings based on completed orders."""
        completed_orders = self.vendor.order_items.filter(order__status='Completed')
        total_earned = sum(order_item.quantity * order_item.price_at_order for order_item in completed_orders)
        self.total_earnings = total_earned
        self.pending_balance = total_earned - self.last_payment
        self.save()
