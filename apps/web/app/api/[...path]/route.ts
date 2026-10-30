import { NextRequest } from "next/server";
export const dynamic = "force-dynamic";
async function proxy(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
) {
  const { path } = await params;
  const url = new URL(
    "/api/" + path.map(encodeURIComponent).join("/") + req.nextUrl.search,
    process.env.API_INTERNAL_URL || "http://127.0.0.1:8000",
  );
  const headers = new Headers();
  for (const name of ["content-type", "cookie", "origin", "x-brain-csrf"]) {
    const v = req.headers.get(name);
    if (v) headers.set(name, v);
  }
  try {
    const upstream = await fetch(url, {
      method: req.method,
      headers,
      body: ["GET", "HEAD"].includes(req.method)
        ? undefined
        : await req.arrayBuffer(),
      cache: "no-store",
      signal: AbortSignal.timeout(30000),
    });
    const out = new Headers({
      "Content-Type":
        upstream.headers.get("content-type") || "application/json",
      "Cache-Control": "no-store",
    });
    const correlation = upstream.headers.get("x-request-id");
    if (correlation) out.set("X-Request-ID", correlation);
    for (const cookie of upstream.headers.getSetCookie())
      out.append("Set-Cookie", cookie);
    return new Response(upstream.body, {
      status: upstream.status,
      headers: out,
    });
  } catch {
    const correlation = crypto.randomUUID();
    return Response.json(
      {
        error: {
          request_id: correlation,
          code: "dependency_unavailable",
          message:
            "The API is unavailable. Check the local services and retry.",
          retryable: true,
        },
      },
      { status: 503, headers: { "X-Request-ID": correlation } },
    );
  }
}
export { proxy as GET, proxy as POST, proxy as PATCH };
