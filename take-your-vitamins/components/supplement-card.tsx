import Link from "next/link"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Supplement } from "@/lib/types"

export function SupplementCard({ supplement }: { supplement: Supplement }) {
  return (
    <Link href={`/supplements/${supplement._id}`}>
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>{supplement.name}</span>
            <Badge variant="outline">{supplement.category}</Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground line-clamp-2">{supplement.description}</p>
        </CardContent>
      </Card>
    </Link>
  )
}

