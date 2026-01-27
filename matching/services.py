import random
from founders.models import FounderProfile

class MatchingService:
    @staticmethod
    def find_roulette_match(current_founder):
        """Find a random founder for video roulette"""
        # Exclude self and get online founders
        candidates = FounderProfile.objects.filter(
            is_online=True
        ).exclude(id=current_founder.id)
        
        # Prefer same stage or complementary skills
        preferred = candidates.filter(stage=current_founder.stage)
        
        if preferred.exists():
            return random.choice(preferred)
        elif candidates.exists():
            return random.choice(candidates)
        return None
    
    @staticmethod
    def calculate_compatibility(founder1, founder2):
        """Calculate compatibility score between two founders"""
        score = 0
        
        # Same stage: +20
        if founder1.stage == founder2.stage:
            score += 20
        
        # Same industry: +15
        if founder1.industry == founder2.industry:
            score += 15
        
        # Complementary skills: +30
        skills1 = set(founder1.skills)
        skills2 = set(founder2.skills)
        complementary = len(skills1.symmetric_difference(skills2))
        score += min(complementary * 10, 30)
        
        # Similar timezone: +20
        # (simplified - you'd want proper timezone calculation)
        if founder1.timezone == founder2.timezone:
            score += 20
        
        # One looking for co-founder: +15
        if 'cofounder' in [founder1.looking_for, founder2.looking_for]:
            score += 15
        
        return min(score, 100)
