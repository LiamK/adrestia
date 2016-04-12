from rest_framework import serializers
from adrestia.models import Candidate, State

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = (
                'state',
                'name',
                'primary_date',
                'general_date',
                )
class CandidateSerializer(serializers.ModelSerializer):
    state = StateSerializer(many=False, read_only=True)
    class Meta:
        model = Candidate
        fields = (
            'name',
            'state',
            'level',
            'office',
            'district',
            'status',
            'serving',
            'running',
            'winner',
            'notes',
            #'primary_date',
            #'legislator',
            #'state_legislator',
            'profile_url',
            'website_url',
            'facebook_url',
            'twitter_url',
            'donate_url',
            'endorsement_url',
            'image_url',
            'image',
        )

