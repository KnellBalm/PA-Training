import Link from "next/link";
import { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-draculaBg text-draculaText flex flex-col">

      {/* --- 상단 Navbar --- */}
      <nav className="w-full h-14 px-6 flex items-center justify-between bg-draculaBg border-b border-draculaBorder">
        <Link href="/" className="text-xl font-bold text-draculaCyan hover:opacity-80">
          Analytics Lab
        </Link>

        <div className="flex items-center gap-4">
          <Link
            href="/generator"
            className="px-3 py-1 rounded bg-draculaPurple hover:bg-draculaPink transition"
          >
            데이터 생성
          </Link>

          <Link
            href="/datasets"
            className="px-3 py-1 rounded bg-draculaPurple hover:bg-draculaPink transition"
          >
            데이터셋 보기
          </Link>
        </div>
      </nav>

      {/* --- 메인 콘텐츠 --- */}
      <main className="flex-1 w-full max-w-[1800px] mx-auto p-6">
        {children}
      </main>
    </div>
  );
}
