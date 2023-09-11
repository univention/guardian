import {type PaginationResponseData} from '@/helpers/models/pagination';

export const getPagination = (totalCount: number, offset: number = 0, limit?: number): PaginationResponseData => {
  return {
    offset: offset,
    limit: limit ?? totalCount,
    total_count: totalCount,
  };
};
