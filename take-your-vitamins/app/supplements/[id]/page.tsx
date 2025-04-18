import { getSupplementById } from "@/lib/supplements"
import { SupplementDetail } from "@/components/supplement-detail"

type Props = {
  params: { id: string }
}

export default async function SupplementPage({ params }: Props) {
  const supplement = await getSupplementById(params.id)

  if (!supplement) {
    return <div> Supplement not found. </div>
  }

  return <SupplementDetail supplement={supplement} />
}