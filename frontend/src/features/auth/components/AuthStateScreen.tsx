import { PageStateMessage } from "@/components/common/PageStateMessage";
import { AuthScreenFrame } from "./AuthScreenFrame";

interface AuthStateScreenProps {
  title: string;
  description: string;
}

export function AuthStateScreen({ title, description }: AuthStateScreenProps) {
  return (
    <AuthScreenFrame>
      <PageStateMessage
        title={title}
        description={description}
        className="flex min-h-40 flex-col items-center justify-center gap-3"
        titleClassName="text-sm"
        descriptionClassName="text-xs text-muted-foreground"
      />
    </AuthScreenFrame>
  );
}
