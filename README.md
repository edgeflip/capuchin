# capuchin

## Development

From the base directory run: `docker-compose up`.

## Production

From the base directory run: `docker-compose -p capuchin -f docker-compose.d/production.yml up -d`.

(The "project name", specified by `-p`, is used as the container names' prefix; depending on the deployment target, this may vary, as `app`, *etc.*.)
