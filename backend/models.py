from django.db import models


class TelegramAccount(models.Model):
    name = models.CharField(verbose_name="Account Name", max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=30, verbose_name="Phone number of merchant")
    merchant_id = models.CharField(max_length=100)
    api_id = models.PositiveBigIntegerField(verbose_name="API ID", null=True, blank=True)
    api_hash = models.CharField(max_length=255, verbose_name="API hash", null=True, blank=True)
    session_string = models.TextField(blank=True, verbose_name="Telegram account session string.")
    chat_id = models.CharField(max_length=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.phone}"


class Contact(models.Model):
    phone = models.CharField(max_length=30, verbose_name="Phone number of client")
    chat_id = models.IntegerField(verbose_name="Chat ID of client.")
    name = models.CharField(max_length=100, verbose_name="Contact name")
    username = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_change = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"+{self.phone} ({self.name})"


class Message(models.Model):
    class Status(models.IntegerChoices):
        UNKNOWN = 0
        SUCCESS = 1
        SERVER_NOT_RECEIVED = 2

    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='contact_messages')
    merchant = models.ForeignKey(TelegramAccount, on_delete=models.CASCADE, related_name='merchant_messages')
    body = models.TextField()
    status = models.IntegerField(choices=Status.choices, default=Status.UNKNOWN)
    msg_id = models.PositiveBigIntegerField("Message ID", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.contact.name} - {self.body}"
