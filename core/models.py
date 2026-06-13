from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    avatar_color = models.CharField(max_length=20, default='#7c3aed')

class DataEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, default='umum')
    data_type = models.CharField(max_length=50, default='text')
    tags = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Analysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data_entry = models.ForeignKey(DataEntry, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=255)
    method = models.CharField(max_length=100, default='statistical')
    result = models.JSONField(blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class AIModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=100, default='classification')
    description = models.TextField(blank=True, null=True)
    config = models.JSONField(default=dict)
    status = models.CharField(max_length=50, default='draft')
    accuracy = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Visualization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    chart_type = models.CharField(max_length=50, default='bar')
    data_source = models.TextField(blank=True, null=True)
    config = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class TrainingSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    dataset = models.CharField(max_length=255, blank=True, null=True)
    epochs = models.IntegerField(default=10)
    progress = models.FloatField(default=0.0)
    status = models.CharField(max_length=50, default='queued')
    log = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class Workflow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    steps = models.JSONField(default=list)
    trigger_type = models.CharField(max_length=50, default='manual')
    status = models.CharField(max_length=50, default='inactive')
    last_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Collaboration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.JSONField(default=list)
    visibility = models.CharField(max_length=50, default='private')
    status = models.CharField(max_length=50, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Dataset(models.Model):
    TIPE_DATA_CHOICES = [
        ('gambar', 'Gambar'),
        ('numerik', 'Numerik'),
        ('teks', 'Teks'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nama_data = models.CharField(max_length=255)
    tipe_data = models.CharField(max_length=20, choices=TIPE_DATA_CHOICES, default='numerik')
    file_upload = models.FileField(upload_to='datasets/', blank=True, null=True)
    content_teks = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nama_data} ({self.tipe_data})"

class Insight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    insight_type = models.CharField(max_length=50, default='observation')
    priority = models.CharField(max_length=50, default='medium')
    status = models.CharField(max_length=50, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

# ============================================================
# INTELLIGENCE SUBMISSION SYSTEM
# (File masuk dari Tim Intelligence Engineer)
# ============================================================

def submission_file_path(instance, filename):
    """Upload path: media/submissions/2026/05/<filename>"""
    from datetime import datetime
    now = datetime.now()
    return f'submissions/{now.year}/{now.month:02d}/{filename}'


class APIKey(models.Model):
    """API Key untuk Tim Engineer agar bisa kirim file via API"""
    key = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=100, help_text="Nama Engineer/Tim")
    email = models.EmailField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(blank=True, null=True)
    usage_count = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def __str__(self):
        return f"{self.name} ({'aktif' if self.is_active else 'nonaktif'})"

    @staticmethod
    def generate_key():
        import secrets
        return secrets.token_urlsafe(48)


class IntelligenceSubmission(models.Model):
    """File yang dikirim Tim Engineer untuk diproses 6 tahap"""

    STAGE_CHOICES = [
        (0, 'Problem Framing & IPO'),
        (1, 'Definisi Dataset'),
        (2, 'Pemrosesan Data'),
        (3, 'Perencanaan Model'),
        (4, 'Pelatihan & Testing'),
        (5, 'Refining Model'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending (Belum Diproses)'),
        ('in_progress', 'Sedang Diproses'),
        ('completed', 'Selesai (6 Tahap Beres)'),
        ('sent', 'Sudah Dikirim ke Tim Lain'),
        ('rejected', 'Ditolak'),
    ]

    DATA_TYPE_CHOICES = [
        ('image', 'Gambar'),
        ('tabular', 'Tabular (CSV/Excel)'),
        ('text', 'Teks'),
        ('numeric', 'Numerik'),
        ('mixed', 'Campuran'),
        ('unknown', 'Belum Terdeteksi'),
    ]

    # === Asal Pengirim ===
    sender_name = models.CharField(max_length=100)
    sender_team = models.CharField(max_length=100, default='Intelligence Engineer')
    sender_email = models.EmailField(blank=True, null=True)
    api_key_used = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='submissions'
    )

    # === Identitas ===
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # === File Utama ===
    source_file = models.FileField(upload_to=submission_file_path)
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.BigIntegerField(default=0)
    detected_data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='unknown'
    )

    # === Metadata Tambahan ===
    extra_metadata = models.JSONField(blank=True, null=True, default=dict)

    # === Tracking ===
    current_stage = models.IntegerField(choices=STAGE_CHOICES, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_to = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assigned_submissions'
    )
    internal_notes = models.TextField(blank=True, null=True)

    # === Timestamps ===
    received_at = models.DateTimeField(auto_now_add=True)
    started_processing_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-received_at']
        verbose_name = 'Intelligence Submission'
        verbose_name_plural = 'Intelligence Submissions'

    def __str__(self):
        return f"[{self.get_status_display()}] {self.title} dari {self.sender_name}"

    @property
    def file_url(self):
        return self.source_file.url if self.source_file else None

    @property
    def progress_percentage(self):
        if self.status in ('completed', 'sent'):
            return 100
        return int((self.current_stage / 6) * 100)
