/**
 * Privacy Policy Page
 * Comprehensive privacy policy based on fintech industry standards
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const PrivacyPolicyPage: React.FC = () => {
  const navigate = useNavigate();
  const lastUpdated = 'January 1, 2025';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded px-2 py-1"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back</span>
          </button>
          <h1 className="text-4xl font-bold text-gray-900">Privacy Policy</h1>
          <p className="text-sm text-gray-600 mt-2">Last Updated: {lastUpdated}</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-lg shadow-sm p-8 space-y-8">
          {/* Introduction */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Introduction</h2>
            <p className="text-gray-700 mb-3">
              SpendSense, Inc. ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains
              how we collect, use, disclose, and safeguard your information when you use our financial literacy platform
              (the "Service").
            </p>
            <p className="text-gray-700">
              By using SpendSense, you consent to the data practices described in this policy. If you do not agree with
              this policy, please discontinue use of our Service.
            </p>
          </section>

          {/* Information We Collect */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Information We Collect</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">2.1 Financial Data</h3>
            <p className="text-gray-700 mb-3">
              When you connect your financial accounts through our secure banking partner, we collect:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li>Transaction history (dates, amounts, merchant names, categories)</li>
              <li>Account balances (checking, savings, credit cards)</li>
              <li>Account metadata (account type, last four digits, institution name)</li>
              <li>Credit limits and utilization rates</li>
              <li>Recurring subscription charges</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">2.2 Personal Information</h3>
            <p className="text-gray-700 mb-3">We collect personal information that you provide to us:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li>Name and email address</li>
              <li>User ID and password (encrypted and hashed)</li>
              <li>Demographic information (age range, location—optional)</li>
              <li>Communication preferences</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">2.3 Usage Data</h3>
            <p className="text-gray-700 mb-3">We automatically collect usage information:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Device information (browser type, operating system, device identifiers)</li>
              <li>Log data (IP address, access times, pages viewed)</li>
              <li>Interaction data (clicks, feature usage, time spent on pages)</li>
              <li>Cookie and tracking technology data</li>
            </ul>
          </section>

          {/* How We Use Your Information */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-700 mb-3">We use your information for the following purposes:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li><strong>Persona Assignment:</strong> Analyzing transaction patterns to match you with a financial persona</li>
              <li><strong>Personalized Recommendations:</strong> Delivering educational content relevant to your financial situation</li>
              <li><strong>Service Improvement:</strong> Understanding how users interact with our platform to enhance features</li>
              <li><strong>Security:</strong> Detecting and preventing fraud, abuse, and security incidents</li>
              <li><strong>Compliance:</strong> Meeting legal and regulatory requirements</li>
              <li><strong>Communications:</strong> Sending service updates, persona changes, and educational content</li>
              <li><strong>Analytics:</strong> Creating aggregated, anonymized reports on financial behavior trends</li>
            </ul>
          </section>

          {/* Data Sharing */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. How We Share Your Information</h2>
            <p className="text-gray-700 mb-3">
              We do not sell your personal financial data. We may share your information in the following circumstances:
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">4.1 Service Providers</h3>
            <p className="text-gray-700 mb-4">
              We work with third-party service providers who perform services on our behalf (e.g., banking data aggregation,
              cloud hosting, analytics). These providers have access to your data only to perform specific tasks and are
              obligated to protect your information.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">4.2 Partner Financial Institutions</h3>
            <p className="text-gray-700 mb-4">
              If you choose to apply for a partner offer (e.g., high-yield savings account), we will share necessary
              information with that institution to process your application. This sharing is always with your explicit consent.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">4.3 Aggregated Analytics</h3>
            <p className="text-gray-700 mb-4">
              We may share aggregated, anonymized data that cannot identify you personally (e.g., "30% of users have
              subscription spending over 10% of income") with researchers, industry partners, or the public.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">4.4 Legal Requirements</h3>
            <p className="text-gray-700 mb-4">
              We may disclose your information if required by law, subpoena, court order, or government request, or if we
              believe disclosure is necessary to protect our rights, your safety, or the safety of others.
            </p>
          </section>

          {/* Data Security */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Data Security</h2>
            <p className="text-gray-700 mb-3">We implement industry-standard security measures to protect your data:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li><strong>Encryption:</strong> 256-bit TLS encryption for data in transit; AES-256 encryption for data at rest</li>
              <li><strong>Access Controls:</strong> Role-based access with multi-factor authentication for employees</li>
              <li><strong>Anonymization:</strong> User identifiers are anonymized and masked in our systems</li>
              <li><strong>Auditing:</strong> Regular security audits and penetration testing</li>
              <li><strong>Monitoring:</strong> 24/7 monitoring for suspicious activity and intrusion attempts</li>
              <li><strong>Token-Based Access:</strong> We never store your bank login credentials; we use revocable read-only tokens</li>
            </ul>
          </section>

          {/* Your Privacy Rights */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Your Privacy Rights</h2>
            <p className="text-gray-700 mb-3">Depending on your location, you may have the following rights:</p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">6.1 Access & Portability</h3>
            <p className="text-gray-700 mb-4">
              You can access and export all your data at any time from the Settings page. We provide data in a machine-readable
              format (JSON) for portability.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">6.2 Correction</h3>
            <p className="text-gray-700 mb-4">
              If your transaction data is incorrect, you can refresh your account connections to re-sync. For personal
              information errors, contact us to request corrections.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">6.3 Deletion (Right to be Forgotten)</h3>
            <p className="text-gray-700 mb-4">
              You can delete your account and all associated data from the Settings page. Deletion is permanent and takes
              effect within 30 days. We may retain certain information if required by law or for legitimate business purposes
              (e.g., fraud prevention).
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">6.4 Opt-Out of Communications</h3>
            <p className="text-gray-700 mb-4">
              You can unsubscribe from marketing emails at any time. Certain service-related communications (e.g., security
              alerts, persona changes) cannot be opted out of while you maintain an account.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">6.5 Withdraw Consent</h3>
            <p className="text-gray-700 mb-4">
              You can revoke SpendSense's access to your financial accounts at any time. This will stop new data collection
              but will not delete historical data unless you also delete your account.
            </p>
          </section>

          {/* Data Retention */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Data Retention</h2>
            <p className="text-gray-700 mb-3">We retain your data as follows:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li><strong>Active Accounts:</strong> Transaction data is retained for up to 2 years to enable historical analysis</li>
              <li><strong>Deleted Accounts:</strong> Data is permanently deleted within 30 days unless required by law</li>
              <li><strong>Anonymized Analytics:</strong> Aggregated data that cannot identify you may be retained indefinitely</li>
              <li><strong>Legal Holds:</strong> Data subject to legal proceedings is retained until the matter is resolved</li>
            </ul>
          </section>

          {/* Cookies & Tracking */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Cookies and Tracking Technologies</h2>
            <p className="text-gray-700 mb-3">We use cookies and similar technologies for:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Authentication and session management</li>
              <li>Remembering your preferences and settings</li>
              <li>Analytics and understanding how users interact with our Service</li>
              <li>Security and fraud prevention</li>
            </ul>
            <p className="text-gray-700 mt-3">
              You can control cookies through your browser settings. Disabling cookies may limit your ability to use
              certain features of the Service.
            </p>
          </section>

          {/* Children's Privacy */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Children's Privacy</h2>
            <p className="text-gray-700">
              SpendSense is not intended for individuals under the age of 18. We do not knowingly collect personal
              information from children. If we become aware that a child has provided us with personal information, we
              will delete it immediately.
            </p>
          </section>

          {/* International Users */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">10. International Data Transfers</h2>
            <p className="text-gray-700">
              SpendSense is based in the United States. If you access our Service from outside the U.S., your information
              may be transferred to, stored, and processed in the U.S. or other countries. By using our Service, you
              consent to this transfer.
            </p>
          </section>

          {/* Changes to This Policy */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Changes to This Privacy Policy</h2>
            <p className="text-gray-700">
              We may update this Privacy Policy from time to time. We will notify you of material changes by email or
              through a prominent notice on our Service. Your continued use of the Service after changes become effective
              constitutes acceptance of the updated policy.
            </p>
          </section>

          {/* Contact Us */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Contact Us</h2>
            <p className="text-gray-700 mb-3">
              If you have questions or concerns about this Privacy Policy, please contact us:
            </p>
            <div className="bg-gray-50 rounded-lg p-4 text-gray-700">
              <p className="font-semibold mb-2">SpendSense, Inc.</p>
              <p>Privacy Officer</p>
              <p>Email: privacy@spendsense.com</p>
              <p>Address: 123 Financial District, San Francisco, CA 94105</p>
            </div>
          </section>

          {/* State-Specific Rights */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">13. State-Specific Privacy Rights</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">13.1 California Residents (CCPA)</h3>
            <p className="text-gray-700 mb-3">If you are a California resident, you have additional rights:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4 mb-4">
              <li>Right to know what personal information we collect and how it's used</li>
              <li>Right to request deletion of your personal information</li>
              <li>Right to opt-out of the sale of personal information (we do not sell data)</li>
              <li>Right to non-discrimination for exercising your privacy rights</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">13.2 European Residents (GDPR)</h3>
            <p className="text-gray-700 mb-3">If you are in the European Economic Area, you have additional rights:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Right to access your personal data</li>
              <li>Right to rectification of inaccurate data</li>
              <li>Right to erasure ("right to be forgotten")</li>
              <li>Right to restrict processing</li>
              <li>Right to data portability</li>
              <li>Right to object to processing</li>
              <li>Right to lodge a complaint with a supervisory authority</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyPage;
