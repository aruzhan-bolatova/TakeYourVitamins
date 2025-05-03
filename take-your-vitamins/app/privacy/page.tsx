import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy | Take Your Vitamins",
  description: "Privacy Policy for Take Your Vitamins application",
};

export default function PrivacyPolicyPage() {
  return (
    <div className="container max-w-4xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-8 text-primary">Privacy Policy</h1>
      
      <div className="prose prose-lg max-w-none">
        <p className="text-lg">Last Updated: {new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</p>
        
        <h2 className="mt-8 text-2xl font-semibold">1. Introduction</h2>
        <p>
          Take Your Vitamins ("we," "our," or "us") is committed to protecting your privacy and ensuring the security 
          of your personal and health information. This Privacy Policy explains how we collect, use, disclose, and 
          safeguard your information when you use our supplement and health tracking application.
        </p>
        
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 my-4">
          <p className="font-semibold text-amber-800">IMPORTANT HEALTH INFORMATION NOTICE</p>
          <p className="text-amber-700">
            This application collects health-related information. While we adhere to strict privacy standards including HIPAA principles 
            and UAE data protection laws, you should always consult with qualified healthcare professionals for medical advice. 
            No digital platform should replace proper medical consultation.
          </p>
        </div>
        
        <h2 className="mt-8 text-2xl font-semibold">2. Information We Collect</h2>
        <p>We may collect the following types of information:</p>
        <ul className="list-disc pl-6">
          <li><strong>Personal Information</strong>: Name, email address, account credentials, and demographic information</li>
          <li><strong>Health Information</strong>: Supplements you take, dosages, frequency, symptom tracking data</li>
          <li><strong>Usage Information</strong>: Device information, IP address, app usage patterns, and analytics data</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">3. How We Use Your Information</h2>
        <p>We use your information for the following purposes:</p>
        <ul className="list-disc pl-6">
          <li>Providing and improving our services</li>
          <li>Personalizing your experience</li>
          <li>Analyzing usage patterns to enhance functionality</li>
          <li>Communicating with you about your account or changes to our services</li>
          <li>Ensuring the security and integrity of our platform</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">4. HIPAA Compliance</h2>
        <p>
          While not all users may be covered entities under HIPAA, we voluntarily apply HIPAA-inspired protections to all health data:
        </p>
        <ul className="list-disc pl-6">
          <li>We implement administrative, physical, and technical safeguards to protect your health information</li>
          <li>We limit internal access to your health information on a need-to-know basis</li>
          <li>We maintain audit trails of access to protected health information</li>
          <li>We conduct regular risk assessments and maintain a breach notification protocol</li>
          <li>We provide mechanisms for you to access, amend, and request deletion of your health information</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">5. UAE Data Protection Compliance</h2>
        <p>
          For users in the United Arab Emirates, we comply with relevant data protection laws and regulations, including:
        </p>
        <ul className="list-disc pl-6">
          <li>Federal Decree-Law No. 45 of 2021 regarding Personal Data Protection</li>
          <li>Federal Law No. 2 of 2019 on the use of ICT in Health Fields</li>
          <li>MOHAP regulations on health data handling and storage</li>
          <li>Dubai Healthcare City (DHCC) and Dubai International Financial Centre (DIFC) data protection standards where applicable</li>
        </ul>
        <p>
          In accordance with UAE regulations, certain health data may be stored on servers within the UAE or in jurisdictions with adequate data protection standards.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">6. Data Sharing and Disclosure</h2>
        <p>We may share your information in the following circumstances:</p>
        <ul className="list-disc pl-6">
          <li><strong>With your consent</strong>: When you explicitly authorize us to share your information</li>
          <li><strong>Service providers</strong>: Third-party vendors who assist in providing our services (all bound by confidentiality obligations)</li>
          <li><strong>Legal requirements</strong>: When required by law, court order, or governmental regulations</li>
          <li><strong>Business transfers</strong>: In connection with a merger, acquisition, or sale of assets</li>
        </ul>
        <p>
          We do <strong>not</strong> sell your personal or health information to third parties for marketing purposes.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">7. Your Rights and Choices</h2>
        <p>You have several rights regarding your personal and health information:</p>
        <ul className="list-disc pl-6">
          <li>Access and review your information</li>
          <li>Update or correct inaccuracies in your information</li>
          <li>Request deletion of your information (subject to certain exceptions)</li>
          <li>Object to certain processing activities</li>
          <li>Request data portability where applicable</li>
          <li>Opt-out of certain communications</li>
        </ul>
        <p>
          To exercise these rights, please contact us using the information provided at the end of this policy.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">8. Data Security</h2>
        <p>
          We implement appropriate technical and organizational measures to protect your information, including:
        </p>
        <ul className="list-disc pl-6">
          <li>Encryption of sensitive personal and health data</li>
          <li>Regular security assessments and vulnerability testing</li>
          <li>Access controls and authentication mechanisms</li>
          <li>Secure data storage and transmission protocols</li>
        </ul>
        <p>
          However, no method of transmission or storage is 100% secure. While we strive to protect your information, 
          we cannot guarantee absolute security.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">9. Children's Privacy</h2>
        <p>
          Our services are not directed to individuals under 18 years of age. We do not knowingly collect personal information
          from children. If you become aware that a child has provided us with personal information, please contact us.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">10. Changes to This Privacy Policy</h2>
        <p>
          We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new 
          Privacy Policy on this page and updating the "Last Updated" date. You are advised to review this Privacy Policy 
          periodically for any changes.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">11. Contact Information</h2>
        <p>
          If you have any questions about this Privacy Policy or our data practices, please contact us at:
          <br />
          <a href="mailto:privacy@takeyourvitamins.com" className="text-primary hover:underline">privacy@takeyourvitamins.com</a>
        </p>
        
        <p className="mt-12 border-t pt-4 text-sm">
          By using Take Your Vitamins, you agree to the collection and use of information in accordance with this Privacy Policy.
        </p>
      </div>
      
      <div className="mt-8">
        <Link 
          href="/" 
          className="text-primary hover:underline flex items-center"
        >
          &larr; Back to home
        </Link>
      </div>
    </div>
  );
} 