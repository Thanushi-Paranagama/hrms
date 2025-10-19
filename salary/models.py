# ============================================
# salary/models.py
# ============================================

from django.db import models

class SalaryRecord(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE, related_name='salary_records')
    
    month = models.IntegerField()
    year = models.IntegerField()
    
    base_salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Attendance based calculations
    days_worked = models.IntegerField(default=0)
    days_absent = models.IntegerField(default=0)
    days_leave = models.IntegerField(default=0)
    
    total_salary = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.month}/{self.year}"

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']

