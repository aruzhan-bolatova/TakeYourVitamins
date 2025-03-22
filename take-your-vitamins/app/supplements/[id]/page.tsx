import { getSupplementById } from "@/lib/supplements"
import { SupplementDetail } from "@/components/supplement-detail"
import { notFound } from "next/navigation"
import type { Metadata } from "next"

interface SupplementPageProps {
  params: {
    id: string
  }
}

export async function generateMetadata({ params }: SupplementPageProps): Promise<Metadata> {
  const supplement = await getSupplementById(params.id)

  if (!supplement) {
    return {
      title: "Supplement Not Found",
    }
  }

  return {
    title: `${supplement.name} - Take Your Vitamins`,
    description: supplement.description,
  }
}

export default async function SupplementPage({ params }: SupplementPageProps) {
  const supplement = await getSupplementById(params.id)

  if (!supplement) {
    notFound()
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <SupplementDetail supplement={supplement} />
    </main>
  )
}

