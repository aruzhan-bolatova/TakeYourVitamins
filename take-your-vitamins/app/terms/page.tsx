import Link from "next/link";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Terms of Service | Take Your Vitamins",
  description: "Terms of Service for Take Your Vitamins application",
};

export default function TermsPage() {
  return (
    <div className="container max-w-4xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-8 text-primary">Terms of Service</h1>
      
      <div className="prose prose-lg max-w-none">
        <p className="text-lg">Last Updated: {new Date().toLocaleDateString("en-US", { month: "long", day: "numeric", year: "numeric" })}</p>
        
        <h2 className="mt-8 text-2xl font-semibold">1. Medical Disclaimer</h2>
        <div className="bg-amber-50 border-l-4 border-amber-500 p-4 my-4">
          <p className="font-semibold text-amber-800">IMPORTANT: Consult Your Healthcare Provider</p>
          <p className="text-amber-700">
            The information provided by Take Your Vitamins is for informational purposes only and is not intended 
            to substitute professional medical advice, diagnosis, or treatment. Always seek the advice of your physician 
            or other qualified healthcare provider with any questions you may have regarding a medical condition, 
            supplement usage, or health objectives.
          </p>
        </div>
        
        <h2 className="mt-8 text-2xl font-semibold">2. About Our Service</h2>
        <p>
          Take Your Vitamins provides tools for tracking supplement intake and health symptoms. Our service is
          designed to help you organize your supplement regimen and monitor potential effects, but should not be
          relied upon for medical decisions.
        </p>
        
        <h2 className="mt-8 text-2xl font-semibold">3. United Arab Emirates Compliance</h2>
        <p>
          Our services comply with relevant UAE regulations regarding digital health applications, including
          Federal Law No. 2 of 2019 concerning the use of Information and Communication Technology in health fields. 
          Users within the UAE should be aware that:
        </p>
        <ul className="list-disc pl-6">
          <li>Supplements tracked in this application may require proper registration with the Ministry of Health and Prevention (MOHAP) to be legally consumed in the UAE</li>
          <li>Health information shared via this platform is subject to UAE privacy and healthcare data regulations</li>
          <li>Any health emergency should be immediately directed to authorized healthcare facilities in the UAE</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">4. HIPAA Compliance</h2>
        <p>
          Take Your Vitamins adheres to the standards set by the Health Insurance Portability and Accountability Act (HIPAA):
        </p>
        <ul className="list-disc pl-6">
          <li>We implement technical, physical, and administrative safeguards to protect your health information</li>
          <li>Your personal health data is encrypted and stored securely</li>
          <li>We do not share your identifiable health information with third parties without your explicit consent</li>
          <li>You can request access to or deletion of your health information at any time</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">5. User Responsibilities</h2>
        <p>
          As a user of this application, you agree to:
        </p>
        <ul className="list-disc pl-6">
          <li>Provide accurate information about your supplement usage and symptoms</li>
          <li>Not rely solely on this application for medical advice or treatment decisions</li>
          <li>Consult with healthcare professionals before starting, changing, or stopping any supplement regimen</li>
          <li>Seek immediate medical attention for any adverse reactions or health concerns</li>
          <li>Keep your account credentials secure and not share access with others</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">6. Limitation of Liability</h2>
        <p>
          Take Your Vitamins and its creators:
        </p>
        <ul className="list-disc pl-6">
          <li>Do not guarantee the accuracy, completeness, or usefulness of information provided</li>
          <li>Are not responsible for any health outcomes related to supplement usage tracked in the application</li>
          <li>Do not endorse specific supplements or treatment regimens</li>
          <li>Disclaim liability for any loss or damage arising from using or relying on the application</li>
        </ul>
        
        <h2 className="mt-8 text-2xl font-semibold">7. Contact Information</h2>
        <p>
          If you have any questions about these Terms of Service, please contact us at:
          <br />
          <a href="mailto:support@takeyourvitamins.com" className="text-primary hover:underline">support@takeyourvitamins.com</a>
        </p>
        
        <p className="mt-12 border-t pt-4 text-sm">
          By using Take Your Vitamins, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
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