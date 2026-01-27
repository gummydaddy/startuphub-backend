from django.contrib.auth.models import AbstractUser
from django.db import models

#initial models for the matching app
class RouletteSession(models.Model):
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='roulette_sessions')
    matched_with = models.ForeignKey('founders.FounderProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='matched_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(default=0)
    connected = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-started_at']


class CofounderMatch(models.Model):
    founder1 = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='matches_as_founder1')
    founder2 = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='matches_as_founder2')
    compatibility_score = models.IntegerField(default=0)  # 0-100
    interested_founder1 = models.BooleanField(default=False)
    interested_founder2 = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['founder1', 'founder2']
        ordering = ['-created_at']

#initial models for the matching app


class MatchFeedback(models.Model):
    match = models.ForeignKey(CofounderMatch, on_delete=models.CASCADE, related_name='feedbacks')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
class DailyMatchStatistic(models.Model):
    date = models.DateField(unique=True)
    total_matches = models.IntegerField(default=0)
    successful_connections = models.IntegerField(default=0)
    average_compatibility_score = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['-date']
class MatchAlgorithmConfig(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parameters = models.JSONField(default=dict)  # e.g., {"weight_skills": 0.5, "weight_personality": 0.5}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['-updated_at']
class MatchNotification(models.Model):
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='match_notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
class MatchPreference(models.Model):
    founder = models.OneToOneField('founders.FounderProfile', on_delete=models.CASCADE, related_name='match_preferences')
    preferred_industries = models.JSONField(default=list)  # e.g., ["Tech", "Health"]
    preferred_stages = models.JSONField(default=list)  # e.g., ["MVP", "Launched"]
    min_compatibility_score = models.IntegerField(default=50)  # 0-100
    
    def __str__(self):
        return f"Match Preferences for {self.founder.name}"
    
    class Meta:
        ordering = ['-founder__created_at']
class MatchSessionLog(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='logs')
    event_type = models.CharField(max_length=100)  # e.g., "match_started", "match_ended"
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict)  # Additional details about the event
    
    class Meta:
        ordering = ['timestamp']
class MatchReferral(models.Model):
    referrer = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE, related_name='sent_referrals')
    referee_email = models.EmailField()
    referee_name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('registered', 'Registered'),
        ('active', 'Active'),
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['referrer', 'referee_email']
        ordering = ['-created_at']
class MatchSuccessStory(models.Model):
    founders = models.ManyToManyField('founders.FounderProfile', related_name='success_stories')
    story = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
class MatchAlgorithmTest(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=dict)  # e.g., {"test_case": "edge_case_1"}
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
class MatchAlgorithmTestResult(models.Model):
    test = models.ForeignKey(MatchAlgorithmTest, on_delete=models.CASCADE, related_name='results')
    passed = models.BooleanField(default=False)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
class MatchSessionRating(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='ratings')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    rating = models.IntegerField()  # 1-5
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
class MatchSessionReport(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
class MatchSessionAnalytics(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='analytics')
    metric_name = models.CharField(max_length=100)  # e.g., "engagement_score"
    metric_value = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
class MatchSessionTag(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)  # e.g., "tech-savvy", "early-stage"
    
    class Meta:
        unique_together = ['session', 'tag']
class MatchSessionReminder(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField()
    message = models.TextField()
    sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['reminder_time']
class MatchSessionLocation(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
class MatchSessionDevice(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='devices')
    device_type = models.CharField(max_length=100)  # e.g., "mobile", "desktop"
    os = models.CharField(max_length=100)  # e.g., "iOS", "Android", "Windows"
    browser = models.CharField(max_length=100)  # e.g., "Chrome", "Firefox"
    
    class Meta:
        ordering = ['-session__started_at']
    def __str__(self):
        return f"Device {self.device_type} for session {self.session.id}"
class MatchSessionDurationBenchmark(models.Model):
    stage = models.CharField(max_length=50)  # e.g., "idea", "mvp", "launched"
    average_duration_seconds = models.IntegerField()
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    def __str__(self):
        return f"Duration Benchmark for {self.stage}"
class MatchSessionEngagementMetric(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='engagement_metrics')
    metric_name = models.CharField(max_length=100)  # e.g., "message_count"
    metric_value = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    def __str__(self):
        return f"Engagement Metric {self.metric_name} for session {self.session.id}"
class MatchSessionFollowUp(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='follow_ups')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    def __str__(self):
        return f"Follow-up by {self.founder.name} for session {self.session.id}"
class MatchSessionOutcome(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='outcomes')
    outcome_type = models.CharField(max_length=100)  # e.g., "connected", "not_connected"
    details = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    def __str__(self):
        return f"Outcome {self.outcome_type} for session {self.session.id}"
class MatchSessionInterest(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='interests')
    founder = models.ForeignKey('founders.FounderProfile', on_delete=models.CASCADE)
    interested = models.BooleanField(default=False)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']
    def __str__(self):
        return f"Interest by {self.founder.name} for session {self.session.id}"
class MatchSessionFeedbackSummary(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='feedback_summaries')
    average_rating = models.FloatField()
    total_feedbacks = models.IntegerField()
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
    def __str__(self):
        return f"Feedback Summary for session {self.session.id}"
class MatchSessionBehaviorAnalysis(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='behavior_analyses')
    behavior_type = models.CharField(max_length=100)  # e.g., "active", "passive"
    analysis_details = models.TextField()
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-analyzed_at']
    def __str__(self):
        return f"Behavior Analysis {self.behavior_type} for session {self.session.id}"
class MatchSessionConnectionAttempt(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='connection_attempts')
    attempt_time = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)
    details = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-attempt_time']
    def __str__(self):
        return f"Connection Attempt for session {self.session.id} at {self.attempt_time}"
class MatchSessionIcebreaker(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='icebreakers')
    question = models.TextField()
    asked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-asked_at']
    def __str__(self):
        return f"Icebreaker for session {self.session.id} asked at {self.asked_at}"
class MatchSessionConversationTopic(models.Model):
    session = models.ForeignKey(RouletteSession, on_delete=models.CASCADE, related_name='conversation_topics')
    topic = models.TextField()
    discussed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-discussed_at']
    def __str__(self):
        return f"Conversation Topic for session {self.session.id} discussed at {self.discussed_at}"
    