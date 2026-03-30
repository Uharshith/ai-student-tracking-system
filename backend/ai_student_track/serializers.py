from rest_framework import serializers
from .models import Subject, Attendance, Marks


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'department', 'year']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'student', 'subject', 'date', 'status']

    def create(self, validated_data):
        user = self.context['request'].user

        try:
            faculty = user.faculty
        except:
            raise serializers.ValidationError("Faculty profile not found")

        return Attendance.objects.create(
            entered_by=faculty,
            **validated_data
        )



class MarksSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(source="subject.name")
    exam_type = serializers.CharField()

    class Meta:
        model = Marks
        fields = [
            "id",
            "subject",
            "exam_type",
            "marks_obtained",
        ]
