# Import necessary modules
from django.db import models
from pygments.lexers import get_all_lexers
from pygments.styles import get_all_styles

# Get a list of available lexers, filtering out those with empty language names
LEXERS = [item for item in get_all_lexers() if item[1]]

# Create choices for languages used in the application
LANGUAGE_CHOICES = sorted([(item[1][0], item[0]) for item in LEXERS])

# Get a list of available styles for syntax highlighting
STYLE_CHOICES = sorted([(item, item) for item in get_all_styles()])


# Define a Django model class called Snippet
class Snippet(models.Model):
    # Field for storing the creation timestamp of the snippet
    created = models.DateTimeField(auto_now_add=True)

    # Field for storing the title of the snippet (maximum length 100 characters)
    title = models.CharField(max_length=100, blank=True, default='')

    # Field for storing the code content of the snippet
    code = models.TextField()

    # Field for indicating whether line numbers should be displayed for the code
    linenos = models.BooleanField(default=False)

    # Field for specifying the programming language of the snippet
    language = models.CharField(choices=LANGUAGE_CHOICES, default='python', max_length=100)

    # Field for specifying the style or theme for displaying the snippet
    style = models.CharField(choices=STYLE_CHOICES, default='friendly', max_length=100)

    # Define the ordering of Snippet instances by their creation timestamp
    class Meta:
        ordering = ['created']
