import { NextResponse } from 'next/server';
export async function POST(req:Request){const b=await req.json().catch(()=>null); if(!b?.eventId) return NextResponse.json({ok:false,status:'failed'},{status:400}); return NextResponse.json({ok:true,status:'acked',eventId:b.eventId});}
