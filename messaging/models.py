from django.db import models
from django.contrib.auth import get_user_model

# User Model Setup
User= get_user_model()
class MessageThread(models.Model):
    participants= models.ManyToManyField(User, related_name='threads')
    created_at= models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)


    # Show readable name of thread in Admin Panel
    def __str__(self):
        participant_names= [user.username for user in self.participants.all()]
        return f"Thread: {', '.join(participant_names)}"


    # Get other Participant
    def get_other_participant(self, current_user):
        return self.participants.exclude(id= current_user.id).first()


    # Get Last Message
    def get_last_message(self):
        return self.messages.order_by('-created_at').first()


# Message Model
class Message(models.Model):
    thread= models.ForeignKey(MessageThread, on_delete= models.CASCADE, related_name='messages')
    sender= models.ForeignKey(User, on_delete= models.CASCADE, related_name= 'sent_messages')
    content= models.TextField()
    is_read= models.BooleanField(default=False)
    created_at= models.DateTimeField(auto_now_add=True)


    # Show Messages in chronological order
    class Meta:
        ordering= ['created_at']

    # Show preview of message in Admin Panel
    def __str__(self):
        return f"Message from{self.sender.username}: {self.content[:50]}..."

    # Mark as read
    def mark_as_read(self):
        self.is_read= True
        self.save()
