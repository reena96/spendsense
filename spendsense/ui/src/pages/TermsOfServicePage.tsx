/**
 * Terms of Service Page
 * Comprehensive terms of service for SpendSense platform
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const TermsOfServicePage: React.FC = () => {
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
          <h1 className="text-4xl font-bold text-gray-900">Terms of Service</h1>
          <p className="text-sm text-gray-600 mt-2">Last Updated: {lastUpdated}</p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="bg-white rounded-lg shadow-sm p-8 space-y-8">
          {/* Acceptance */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-700 mb-3">
              Welcome to SpendSense. These Terms of Service ("Terms") govern your access to and use of the SpendSense
              platform, website, and mobile applications (collectively, the "Service"). By creating an account or using
              the Service, you agree to be bound by these Terms.
            </p>
            <p className="text-gray-700">
              If you do not agree to these Terms, you may not access or use the Service. We reserve the right to modify
              these Terms at any time, and will notify you of material changes.
            </p>
          </section>

          {/* Eligibility */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">2. Eligibility</h2>
            <p className="text-gray-700 mb-3">To use SpendSense, you must:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Be at least 18 years of age</li>
              <li>Have the legal capacity to enter into a binding agreement</li>
              <li>Not be prohibited from using the Service under applicable laws</li>
              <li>Provide accurate and complete information during registration</li>
              <li>Maintain the security of your account credentials</li>
            </ul>
          </section>

          {/* Account Registration */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">3. Account Registration and Security</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">3.1 Account Creation</h3>
            <p className="text-gray-700 mb-4">
              You must create an account to use certain features of the Service. You agree to provide accurate, current,
              and complete information and to update your information as necessary to keep it accurate and complete.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">3.2 Account Security</h3>
            <p className="text-gray-700 mb-4">
              You are responsible for maintaining the confidentiality of your account credentials and for all activities
              that occur under your account. You must notify us immediately of any unauthorized access or use of your account.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">3.3 One Account Per Person</h3>
            <p className="text-gray-700 mb-4">
              Each user may maintain only one account. Creating multiple accounts may result in suspension or termination
              of all accounts.
            </p>
          </section>

          {/* Service Description */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">4. Description of Service</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">4.1 What We Provide</h3>
            <p className="text-gray-700 mb-4">
              SpendSense is a financial literacy platform that analyzes your transaction data to provide personalized
              educational content and recommendations. We assign you to a financial persona based on behavioral signals
              and deliver relevant articles, tools, and partner offers.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">4.2 What We Don't Provide</h3>
            <p className="text-gray-700 mb-3">
              SpendSense is NOT a financial advisor, investment platform, or banking service. We do not:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Provide personalized financial, investment, or legal advice</li>
              <li>Execute transactions or move money on your behalf</li>
              <li>Guarantee any financial outcomes or returns</li>
              <li>Endorse any specific financial products (including partner offers)</li>
              <li>Act as a fiduciary or have a duty to maximize your financial outcomes</li>
            </ul>
          </section>

          {/* Financial Data Access */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">5. Financial Data Access and Consent</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">5.1 Read-Only Access</h3>
            <p className="text-gray-700 mb-4">
              When you connect your financial accounts, you grant SpendSense read-only access to your transaction history,
              account balances, and related metadata. We cannot and will not move money, make purchases, or execute
              transactions on your behalf.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">5.2 Third-Party Data Aggregators</h3>
            <p className="text-gray-700 mb-4">
              We use third-party banking data aggregation services to securely connect to your financial institutions.
              By using our Service, you also agree to the terms and conditions of these third-party providers.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">5.3 Revoking Access</h3>
            <p className="text-gray-700 mb-4">
              You may revoke SpendSense's access to your financial accounts at any time through your account settings.
              Revoking access will prevent us from collecting new transaction data but will not delete historical data
              unless you also delete your account.
            </p>
          </section>

          {/* Acceptable Use */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">6. Acceptable Use Policy</h2>
            <p className="text-gray-700 mb-3">You agree NOT to:</p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Use the Service for any unlawful purpose or in violation of any laws</li>
              <li>Attempt to gain unauthorized access to our systems or other users' accounts</li>
              <li>Reverse engineer, decompile, or disassemble any part of the Service</li>
              <li>Use automated tools (bots, scrapers) to access the Service without permission</li>
              <li>Upload malicious code, viruses, or harmful content</li>
              <li>Impersonate any person or entity or misrepresent your affiliation</li>
              <li>Interfere with or disrupt the integrity or performance of the Service</li>
              <li>Share your account credentials with others</li>
              <li>Use the Service to spam, harass, or send unsolicited communications</li>
            </ul>
          </section>

          {/* Intellectual Property */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">7. Intellectual Property Rights</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">7.1 Our Content</h3>
            <p className="text-gray-700 mb-4">
              All content, features, and functionality of the Service (including text, graphics, logos, icons, software,
              and algorithms) are owned by SpendSense and protected by copyright, trademark, and other intellectual
              property laws. You may not reproduce, distribute, or create derivative works without our express permission.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">7.2 Your Data</h3>
            <p className="text-gray-700 mb-4">
              You retain ownership of your financial data. By using the Service, you grant us a limited license to use
              your data solely for the purposes described in our Privacy Policy (persona assignment, recommendations,
              aggregated analytics).
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">7.3 Feedback</h3>
            <p className="text-gray-700 mb-4">
              If you provide feedback, suggestions, or ideas about the Service, you grant us a perpetual, worldwide,
              royalty-free license to use and incorporate such feedback without compensation or attribution.
            </p>
          </section>

          {/* Disclaimers */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">8. Disclaimers and Limitations</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">8.1 No Financial Advice</h3>
            <p className="text-gray-700 mb-4">
              <strong>IMPORTANT:</strong> SpendSense provides educational content only, not financial advice. All
              recommendations are general in nature and may not be suitable for your specific circumstances. You should
              consult a licensed financial advisor before making financial decisions.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">8.2 No Warranties</h3>
            <p className="text-gray-700 mb-4">
              THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED,
              INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
              NON-INFRINGEMENT. We do not guarantee that the Service will be uninterrupted, error-free, or secure.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">8.3 Data Accuracy</h3>
            <p className="text-gray-700 mb-4">
              We strive for accuracy but cannot guarantee that transaction data, categorization, or behavioral signals
              are 100% accurate. Data quality depends on the information provided by your financial institutions and
              third-party aggregators.
            </p>
          </section>

          {/* Limitation of Liability */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">9. Limitation of Liability</h2>
            <p className="text-gray-700 mb-3">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, SPENDSENSE SHALL NOT BE LIABLE FOR:
            </p>
            <ul className="list-disc list-inside text-gray-700 space-y-2 ml-4">
              <li>Indirect, incidental, special, consequential, or punitive damages</li>
              <li>Loss of profits, revenue, data, or business opportunities</li>
              <li>Financial losses resulting from reliance on our educational content</li>
              <li>Errors in transaction data or persona assignments</li>
              <li>Unauthorized access to your account due to your failure to secure credentials</li>
              <li>Third-party actions (including banking institutions, data aggregators, or partner offers)</li>
            </ul>
            <p className="text-gray-700 mt-3">
              OUR TOTAL LIABILITY TO YOU SHALL NOT EXCEED THE AMOUNT YOU PAID TO SPENDSENSE IN THE 12 MONTHS PRECEDING
              THE CLAIM (OR $100 IF YOU HAVE NOT PAID US ANYTHING).
            </p>
          </section>

          {/* Indemnification */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">10. Indemnification</h2>
            <p className="text-gray-700">
              You agree to indemnify, defend, and hold harmless SpendSense, its officers, directors, employees, and
              agents from any claims, losses, damages, liabilities, and expenses (including attorney fees) arising from:
              (a) your use of the Service, (b) your violation of these Terms, (c) your violation of any third-party
              rights, or (d) any unauthorized access to your account resulting from your failure to protect your credentials.
            </p>
          </section>

          {/* Termination */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">11. Termination</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">11.1 Termination by You</h3>
            <p className="text-gray-700 mb-4">
              You may terminate your account at any time by deleting your account through the Settings page. Upon
              termination, your data will be deleted within 30 days as described in our Privacy Policy.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">11.2 Termination by Us</h3>
            <p className="text-gray-700 mb-4">
              We may suspend or terminate your access to the Service at any time, with or without notice, if we believe
              you have violated these Terms, engaged in fraudulent activity, or for any other reason at our sole discretion.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">11.3 Effect of Termination</h3>
            <p className="text-gray-700 mb-4">
              Upon termination, your right to use the Service immediately ceases. Sections of these Terms that by their
              nature should survive termination (including disclaimers, limitations of liability, and indemnification)
              will remain in effect.
            </p>
          </section>

          {/* Dispute Resolution */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">12. Dispute Resolution and Arbitration</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">12.1 Informal Resolution</h3>
            <p className="text-gray-700 mb-4">
              If you have a dispute with SpendSense, you agree to first contact us at legal@spendsense.com to attempt
              to resolve the issue informally before pursuing formal legal action.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">12.2 Binding Arbitration</h3>
            <p className="text-gray-700 mb-4">
              Any disputes that cannot be resolved informally shall be resolved through binding arbitration in accordance
              with the American Arbitration Association's rules. You waive your right to a jury trial and to participate
              in class actions.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">12.3 Exceptions</h3>
            <p className="text-gray-700 mb-4">
              Either party may seek injunctive relief in court to prevent actual or threatened infringement of intellectual
              property rights. Small claims court actions are also exempt from the arbitration requirement.
            </p>
          </section>

          {/* Governing Law */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">13. Governing Law and Jurisdiction</h2>
            <p className="text-gray-700">
              These Terms are governed by the laws of the State of California, without regard to conflict of law principles.
              Any legal action not subject to arbitration shall be brought exclusively in the state or federal courts
              located in San Francisco, California.
            </p>
          </section>

          {/* Miscellaneous */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">14. Miscellaneous Provisions</h2>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">14.1 Entire Agreement</h3>
            <p className="text-gray-700 mb-4">
              These Terms, together with our Privacy Policy, constitute the entire agreement between you and SpendSense
              regarding the Service.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">14.2 Severability</h3>
            <p className="text-gray-700 mb-4">
              If any provision of these Terms is found to be unenforceable, the remaining provisions will remain in full
              force and effect.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">14.3 No Waiver</h3>
            <p className="text-gray-700 mb-4">
              Our failure to enforce any provision of these Terms does not constitute a waiver of that provision or any
              other provision.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">14.4 Assignment</h3>
            <p className="text-gray-700 mb-4">
              You may not assign or transfer these Terms or your account without our prior written consent. We may assign
              these Terms without restriction.
            </p>

            <h3 className="text-xl font-semibold text-gray-900 mb-3">14.5 Changes to Terms</h3>
            <p className="text-gray-700 mb-4">
              We may modify these Terms at any time. Material changes will be notified via email or prominent notice on
              the Service. Your continued use after changes become effective constitutes acceptance.
            </p>
          </section>

          {/* Contact */}
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-4">15. Contact Information</h2>
            <p className="text-gray-700 mb-3">
              If you have questions about these Terms, please contact us:
            </p>
            <div className="bg-gray-50 rounded-lg p-4 text-gray-700">
              <p className="font-semibold mb-2">SpendSense, Inc.</p>
              <p>Legal Department</p>
              <p>Email: legal@spendsense.com</p>
              <p>Address: 123 Financial District, San Francisco, CA 94105</p>
            </div>
          </section>

          {/* Acknowledgment */}
          <section className="bg-cyan-50 border border-cyan-200 rounded-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Acknowledgment</h2>
            <p className="text-gray-700">
              BY USING SPENDSENSE, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND AGREE TO BE BOUND BY THESE TERMS
              OF SERVICE. IF YOU DO NOT AGREE, YOU MUST NOT USE THE SERVICE.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
};

export default TermsOfServicePage;
