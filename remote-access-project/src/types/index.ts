export interface RequestData {
    id: string;
    payload: any;
}

export interface ResponseData {
    success: boolean;
    message: string;
    data?: any;
}