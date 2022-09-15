# Training Studio App UI

This guide explains the process of: installing the dependencies for, building, and developing the Training Studio App React UI.

## Installing Dependencies

Before you can build the UI, you will need to install:
- [node.js](https://nodejs.org/en/)
- [yarn](https://yarnpkg.com/getting-started/install)

Once you have yarn installed, you can install the dependencies for this project by running (from the `lightning_hpo/app/ui` folder):
```bash
yarn install
```

## Building the UI

To build the UI, run:
```bash
yarn run build
```

## Running the App

To run the app with the react UI, use:
```bash
REACT_UI=1 lightning run app ...
```

**Note: You can rebuild the UI and refresh the app page without stopping the app.**

## Updating the App Client

If the app REST API changes, update `spec.json` to the new openapi spec and re-generate the client with:
```bash
yarn run generate
```

## Live Building

If you want the UI to live update, run:
```bash
yarn run start
```

**Note: This is not generally recommended as it can be quite resource intensive.**
