from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from employees.models import Employee
from .models import LeaveType, LeaveRequest
from datetime import date, timedelta


class TestStaffApproval(TestCase):
	def setUp(self):
		# Leave owner (has Employee profile)
		self.owner_user = User.objects.create_user(username='owner', password='ownerpass', first_name='Owner', last_name='User', email='owner@example.com')
		self.owner_emp = Employee.objects.create(user=self.owner_user, employee_id='EMP100')

		# Leave type
		self.leave_type = LeaveType.objects.create(name='Sick Leave')

		# Create a pending leave request
		self.leave = LeaveRequest.objects.create(
			employee=self.owner_emp,
			leave_type=self.leave_type,
			start_date=date.today() + timedelta(days=1),
			end_date=date.today() + timedelta(days=1),
			days_requested=1,
			reason='Test leave'
		)

		# Staff user without Employee profile
		self.staff_user = User.objects.create_user(username='staff', password='staffpass', is_staff=True)

	def test_staff_can_approve_leave_without_employee_profile(self):
		# Login as staff
		self.client.login(username='staff', password='staffpass')

		url = reverse('leave_request_approve', args=[self.leave.id])
		resp = self.client.post(url, {'action': 'approve'}, follow=True)

		self.leave.refresh_from_db()
		self.assertEqual(self.leave.status, 'APPROVED')
		# approved_by should be None because approver has no Employee profile
		self.assertIsNone(self.leave.approved_by)
		self.assertIsNotNone(self.leave.approval_date)
		# Redirect to list
		self.assertEqual(resp.status_code, 200)
