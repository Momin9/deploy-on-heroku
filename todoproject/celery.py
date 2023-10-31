# import os
#
# from celery import Celery
# from celery.schedules import crontab
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_home_41612.settings')
#
# app = Celery('rest_project')
# app.config_from_object('django.conf:settings')
# app.autodiscover_tasks()
#
#
# app.conf.beat_schedule = {
#     'delete_old_stats': {
#         'task': 'modules.statistics_app.tasks.delete_old_stats',
#         'schedule': 3601,
#     },
#     'check_device_status': {
#         'task': 'home.tasks.check_device_status',
#         'schedule': 60,
#     },
#     'count_down_timer': {
#         'task': 'modules.timer_app.tasks.count_down_timer',
#         'schedule': 20,
#     },
#     'change_state_on_timer': {
#         'task': 'modules.timer_app.tasks.change_state_on_timer',
#         'schedule': 20,
#     },
#     'save_hourly_average_values_in_stats': {
#         'task': 'modules.statistics_app.tasks.save_hourly_average_values_in_stats',
#         'schedule': 3601,
#     },
#     'save_average_daily_stats': {
#         'task': 'modules.statistics_app.tasks.save_average_daily_stats',
#         'schedule': crontab(hour=5, minute=1),
#     },
#     'save_average_weekly_stats': {
#         'task': 'modules.statistics_app.tasks.save_average_weekly_stats',
#         'schedule': crontab(day_of_week=1, hour=5, minute=1),
#     },
#     'save_average_monthly_stats': {
#         'task': 'modules.statistics_app.tasks.save_average_monthly_stats',
#         'schedule': crontab(day_of_month=1, hour=5, minute=1),
#     },
#     'save_average_yearly_stats': {
#         'task': 'modules.statistics_app.tasks.save_average_yearly_stats',
#         'schedule': crontab(month_of_year=1, hour=5, minute=1),
#     },
# }
