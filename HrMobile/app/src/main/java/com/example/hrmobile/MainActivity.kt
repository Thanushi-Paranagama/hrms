package com.example.hrmobile

import android.content.Intent
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputEditText

class MainActivity : AppCompatActivity() {

    private lateinit var usernameInput: TextInputEditText
    private lateinit var passwordInput: TextInputEditText
    private lateinit var loginButton: MaterialButton
    private lateinit var registerButton: MaterialButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize views
        usernameInput = findViewById(R.id.usernameInput)
        passwordInput = findViewById(R.id.passwordInput)
        loginButton = findViewById(R.id.loginButton)
        registerButton = findViewById(R.id.registerButton)

        // Set up login button click listener
        loginButton.setOnClickListener {
            handleLogin()
        }

        // Set up register button click listener
        registerButton.setOnClickListener {
            // Navigate to registration activity
            val intent = Intent(this, RegistrationActivity::class.java)
            startActivity(intent)
        }
    }

    private fun handleLogin() {
        val username = usernameInput.text.toString().trim()
        val password = passwordInput.text.toString().trim()

        // Validate empty fields
        if (username.isEmpty()) {
            usernameInput.error = "Username is required"
            usernameInput.requestFocus()
            return
        }

        if (password.isEmpty()) {
            passwordInput.error = "Password is required"
            passwordInput.requestFocus()
            return
        }

        // Validate credentials (hardcoded for testing)
        // Replace this with your actual authentication logic (database, API, etc.)
        if (isValidCredentials(username, password)) {
            // Login successful
            Toast.makeText(this, "Login Successful!", Toast.LENGTH_SHORT).show()

            // Navigate to Dashboard
            val intent = Intent(this, DashboardActivity::class.java)
            intent.putExtra("USERNAME", username) // Pass username to dashboard
            startActivity(intent)
            finish() // Close login activity so user can't go back with back button
        } else {
            // Login failed
            Toast.makeText(this, "Invalid username or password", Toast.LENGTH_SHORT).show()
            passwordInput.error = "Invalid credentials"
        }
    }

    // Validate credentials - Replace this with your actual authentication
    private fun isValidCredentials(username: String, password: String): Boolean {
        // Example hardcoded credentials for testing
        // TODO: Replace with database or API authentication
        return username == "emp" && password == "111222"

        // OR for multiple users:
        // val validUsers = mapOf(
        //     "admin" to "admin123",
        //     "user1" to "password1",
        //     "1212" to "1212"
        // )
        // return validUsers[username] == password
    }
}