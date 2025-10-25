from django.db import models
from django.conf import settings


class Subject(models.Model):
    """
    Subject model for storing learning subjects.
    """
    LEVEL_BEGINNER = "beginner"
    LEVEL_INTERMEDIATE = "intermediate"
    LEVEL_ADVANCED = "advanced"
    LEVEL_EXPERT = "expert"
    
    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, "Beginner"),
        (LEVEL_INTERMEDIATE, "Intermediate"),
        (LEVEL_ADVANCED, "Advanced"),
        (LEVEL_EXPERT, "Expert"),
    ]
    
    code = models.TextField(unique=True, db_index=True, help_text="Unique subject code")
    name_vi = models.TextField(help_text="Subject name in Vietnamese")
    name_en = models.TextField(help_text="Subject name in English")
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, null=True, blank=True, help_text="Subject difficulty level")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "subjects"
        ordering = ["-created_at"]
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __str__(self):
        return f"{self.code} - {self.name_en}"


class UserSubject(models.Model):
    """
    UserSubject model for tracking user's learning subjects.
    """
    LEVEL_BEGINNER = "beginner"
    LEVEL_INTERMEDIATE = "intermediate"
    LEVEL_ADVANCED = "advanced"
    LEVEL_EXPERT = "expert"
    
    LEVEL_CHOICES = [
        (LEVEL_BEGINNER, "Beginner"),
        (LEVEL_INTERMEDIATE, "Intermediate"),
        (LEVEL_ADVANCED, "Advanced"),
        (LEVEL_EXPERT, "Expert"),
    ]
    
    INTENT_LEARN = "learn"
    INTENT_TEACH = "teach"
    INTENT_BOTH = "both"
    
    INTENT_CHOICES = [
        (INTENT_LEARN, "Learn"),
        (INTENT_TEACH, "Teach"),
        (INTENT_BOTH, "Both"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_subjects",
        db_column="user_id"
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="user_subjects",
        db_column="subject_id"
    )
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, help_text="User's level in this subject")
    intent = models.CharField(max_length=50, choices=INTENT_CHOICES, help_text="User's intent (learn/teach/both)")
    note = models.TextField(blank=True, default="", help_text="Additional notes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "user_subjects"
        ordering = ["-created_at"]
        unique_together = [["user", "subject"]]
        verbose_name = "User Subject"
        verbose_name_plural = "User Subjects"
    
    def __str__(self):
        return f"{self.user.email} - {self.subject.code} ({self.intent})"


class Goal(models.Model):
    """
    Goal model for storing learning goals.
    """
    TYPE_DAILY = "daily"
    TYPE_WEEKLY = "weekly"
    TYPE_MONTHLY = "monthly"
    TYPE_YEARLY = "yearly"
    TYPE_MILESTONE = "milestone"
    
    TYPE_CHOICES = [
        (TYPE_DAILY, "Daily"),
        (TYPE_WEEKLY, "Weekly"),
        (TYPE_MONTHLY, "Monthly"),
        (TYPE_YEARLY, "Yearly"),
        (TYPE_MILESTONE, "Milestone"),
    ]
    
    code = models.TextField(unique=True, db_index=True, help_text="Unique goal code")
    name = models.TextField(help_text="Goal name/description")
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, help_text="Goal type (daily/weekly/monthly/etc.)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "goals"
        ordering = ["-created_at"]
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class UserGoal(models.Model):
    """
    UserGoal model for tracking user's learning goals.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_goals",
        db_column="user_id"
    )
    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        related_name="user_goals",
        db_column="goal_id"
    )
    target_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Target value for the goal")
    target_date = models.DateField(help_text="Target completion date")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "user_goals"
        ordering = ["-created_at"]
        unique_together = [["user", "goal"]]
        verbose_name = "User Goal"
        verbose_name_plural = "User Goals"
    
    def __str__(self):
        return f"{self.user.email} - {self.goal.code} (Target: {self.target_value})"
