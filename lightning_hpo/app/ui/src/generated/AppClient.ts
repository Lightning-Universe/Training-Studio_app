/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { AxiosHttpRequest } from './core/AxiosHttpRequest';

import { AppClientCommandService } from './services/AppClientCommandService';
import { AppCommandService } from './services/AppCommandService';
import { DefaultService } from './services/DefaultService';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class AppClient {

    public readonly appClientCommand: AppClientCommandService;
    public readonly appCommand: AppCommandService;
    public readonly default: DefaultService;

    public readonly request: BaseHttpRequest;

    constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = AxiosHttpRequest) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? '',
            VERSION: config?.VERSION ?? '0.1.0',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });

        this.appClientCommand = new AppClientCommandService(this.request);
        this.appCommand = new AppCommandService(this.request);
        this.default = new DefaultService(this.request);
    }
}
