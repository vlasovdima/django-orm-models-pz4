from django.contrib import admin

from .models import Course, Department, StudentProfile


# Отображение списка факультетов с поиском по названию
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# Настройка панели курсов: фильтр по факультету и поиск по названию дисциплины
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'department')
    list_filter = ('department',)
    search_fields = ('title',)


# Панель профилей студентов с горизонтальным виджетом выбора курсов (N:M)
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'department')
    list_filter = ('department',)
    search_fields = ('user__username',)
    filter_horizontal = ('courses',)
