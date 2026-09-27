/**
 * Contract tests for lib/api.ts — run with a stubbed global fetch so no
 * backend is needed. Verifies envelope parsing, NOT_IMPLEMENTED handling,
 * auth headers and that the base URL comes only from NEXT_PUBLIC_API_BASE_URL.
 */
const ORIGINAL_ENV = process.env;

/** Minimal Response stand-in (jsdom does not ship the fetch Response class). */
function jsonResponse(status: number, body: unknown) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(body),
  };
}

function stubFetch(status: number, body: unknown) {
  const fetchMock = jest.fn().mockResolvedValue(jsonResponse(status, body));
  global.fetch = fetchMock as unknown as typeof fetch;
  return fetchMock;
}

describe("api client", () => {
  // lib/config.ts reads the env var at import time — reset modules per test
  // and import dynamically AFTER setting the env.
  let api: typeof import("@/lib/api").api;

  beforeEach(async () => {
    jest.resetModules();
    process.env = { ...ORIGINAL_ENV };
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://api.test";
    ({ api } = await import("@/lib/api"));
  });

  afterAll(() => {
    process.env = ORIGINAL_ENV;
  });

  it("parses the error envelope into ApiError (501 NOT_IMPLEMENTED)", async () => {
    stubFetch(501, {
      error: {
        code: "NOT_IMPLEMENTED",
        message: "Clustering pipeline not implemented",
        details: null,
      },
    });

    await expect(api.listClusters()).rejects.toMatchObject({
      name: "ApiError",
      status: 501,
      code: "NOT_IMPLEMENTED",
      message: "Clustering pipeline not implemented",
    });
  });

  it("sends Authorization header when a token is given", async () => {
    const fetchMock = stubFetch(200, { access_token: "t", role: "analyst" });

    await api.getCluster(1, "tok123");

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer tok123");
    expect(String(fetchMock.mock.calls[0][0])).toBe("http://api.test/clusters/1");
  });

  it("builds query params for listClusters", async () => {
    const fetchMock = stubFetch(200, { items: [], total: 0 });

    await api.listClusters({ district: "pune", status: "flagged" });

    expect(String(fetchMock.mock.calls[0][0])).toContain("district=pune");
    expect(String(fetchMock.mock.calls[0][0])).toContain("status=flagged");
  });
});
