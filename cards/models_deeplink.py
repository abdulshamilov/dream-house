from django.db import models


class DeepLinkConfig(models.Model):
    """
    Синглтон-модель для настроек Deep Links.
    Редактируется через Django Admin — без деплоя.
    """

    # --- iOS ---
    ios_team_id = models.CharField(
        "Apple Team ID",
        max_length=20,
        default="48RARN99NS",
        help_text="Team ID из Apple Developer Account",
    )
    ios_bundle_id = models.CharField(
        "iOS Bundle ID",
        max_length=100,
        default="com.dreamhouse.app",
    )
    appstore_url = models.URLField(
        "App Store URL",
        max_length=500,
        default="https://apps.apple.com/app/dreamhouse/id000000000",
        help_text="Ссылка на приложение в App Store",
    )

    # --- Android ---
    android_package_name = models.CharField(
        "Android Package Name",
        max_length=100,
        default="com.dreamhouse.app",
    )
    android_sha256_fingerprint = models.CharField(
        "SHA-256 Fingerprint",
        max_length=200,
        default="SHA256_ОТПЕЧАТОК_ВАШЕГО_КЛЮЧА",
        help_text="SHA-256 отпечаток signing key из Google Play Console",
    )
    playstore_url = models.URLField(
        "Google Play URL",
        max_length=500,
        default="https://play.google.com/store/apps/details?id=com.dreamhouse.app",
        help_text="Ссылка на приложение в Google Play",
    )

    # --- Deep Link paths ---
    deep_link_paths = models.CharField(
        "Пути для deep links",
        max_length=500,
        default="/ref/*",
        help_text="Через запятую, например: /ref/*, /invite/*",
    )

    class Meta:
        verbose_name = "Настройка Deep Links"
        verbose_name_plural = "Настройки Deep Links"

    def __str__(self):
        return "Deep Link Configuration"

    def save(self, *args, **kwargs):
        # Синглтон: всегда id=1, нельзя создать вторую запись
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Получить или создать единственную запись."""
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    # --- Генерация JSON ---

    def get_apple_app_site_association(self):
        paths = [p.strip() for p in self.deep_link_paths.split(",")]
        return {
            "applinks": {
                "apps": [],
                "details": [
                    {
                        "appID": f"{self.ios_team_id}.{self.ios_bundle_id}",
                        "paths": paths,
                    }
                ],
            }
        }

    def get_asset_links(self):
        return [
            {
                "relation": ["delegate_permission/common.handle_all_urls"],
                "target": {
                    "namespace": "android_app",
                    "package_name": self.android_package_name,
                    "sha256_cert_fingerprints": [
                        self.android_sha256_fingerprint,
                    ],
                },
            }
        ]
