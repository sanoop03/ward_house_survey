from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Extended User model supporting two roles: admin and field_agent.
    """

    ROLE_ADMIN = 'admin'
    ROLE_FIELD_AGENT = 'field_agent'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_FIELD_AGENT, 'Field Agent'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_FIELD_AGENT,
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_field_agent(self):
        return self.role == self.ROLE_FIELD_AGENT
