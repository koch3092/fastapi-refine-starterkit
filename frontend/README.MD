# Frontend

## Getting Started

This is the Refine admin console for the FastAPI starterkit. It uses React,
TypeScript, Vite, shadcn/ui, Tailwind CSS, and `@refinedev/simple-rest`.

## Available Scripts

### Running the development server.

```bash
    npm run dev
```

### Building for production.

```bash
    npm run build
```

### Running the production server.

```bash
    npm run start
```

## Learn More

This project uses `@refinedev/simple-rest` as the global data provider. Set
`VITE_API_URL` to the backend origin, for example `http://localhost:8000`; the app
adds `/api/v1` in `src/providers/constants.ts`.

The default `assets` resource provides list/show/delete pages and a presigned upload
flow. The frontend asks the backend for `/assets/presigned-upload`, then uploads the
selected file directly to S3/MinIO with the returned URL and headers.

OpenAPI generation is type-only. `bash ../scripts/generate-client.sh` writes
`openapi.json` and generates only `src/client/index.ts`, `src/client/schemas.gen.ts`,
and `src/client/types.gen.ts`.

To learn more about **Refine**, please check out the [Documentation](https://refine.dev/docs)

- **REST Data Provider** [Docs](https://refine.dev/docs/core/providers/data-provider/#overview)
- **Refine shadcn/ui** [Docs](https://refine.dev/docs/ui-integrations/shadcn-ui/)
- **React Router** [Docs](https://refine.dev/docs/core/providers/router-provider/)
- **Custom Auth Provider** [Docs](https://refine.dev/docs/core/providers/auth-provider/)

## License

MIT
