import random
from faker import Faker
from blog.models import Blog
from accounts.models import User


def generate_fake_blogs(num_blogs):
    fake = Faker()

    # Create some fake users
    users = User.objects.all()

    # Create some fake blog categories

    for i in range(num_blogs):
        # Randomly select a user and category
        user = random.choice(users)

        # Generate fake data
        title = fake.sentence()
        content = fake.paragraphs(nb=3)

        # Create the blog object
        blog = Blog.objects.create(
            user=user,
            title=title,
            content=content,
            is_active=True,
            is_validated=True
        )
